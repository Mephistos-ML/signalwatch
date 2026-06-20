"""TK Maxx source implementation."""

from __future__ import annotations

import re
from collections.abc import Sequence
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from bs4.element import Tag
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from signalwatch.models import WatchItem

DEFAULT_TIMEOUT_MILLISECONDS = 30_000
PRODUCT_CARD_SELECTOR = "li.c-product-grid__item"
PRODUCT_ID_PATTERN = re.compile(r"/p/(\d+)")
GBP_PATTERN = re.compile(r"£\s*([0-9][0-9,]*(?:\.[0-9]+)?)")
RRP_PATTERN = re.compile(r"\bRRP\s*£\s*([0-9][0-9,]*(?:\.[0-9]+)?)", re.IGNORECASE)
SAVING_PATTERN = re.compile(r"\bsave\s*£\s*([0-9][0-9,]*(?:\.[0-9]+)?)", re.IGNORECASE)
PERCENT_PATTERN = re.compile(r"-?\s*([0-9]+(?:\.[0-9]+)?)\s*%")


class TkMaxxSource:
    """Source for TK Maxx product listing pages."""

    def __init__(self, url: str) -> None:
        """Initialise the TK Maxx source.

        Args:
            url: TK Maxx listing page URL.
        """
        self.url = url

    def fetch_items(self) -> Sequence[WatchItem]:
        """Fetch and normalise TK Maxx items.

        Returns:
            Normalised watch items extracted from the TK Maxx listing page.
        """
        html = self._fetch_html()
        return _extract_items_from_html(html=html, base_url=self.url)

    def _fetch_html(self) -> str:
        """Fetch the configured TK Maxx listing page HTML using a browser render.

        Returns:
            Rendered HTML page content.
        """
        with sync_playwright() as playwright:
            browser = playwright.webkit.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(
                    self.url,
                    wait_until="domcontentloaded",
                    timeout=DEFAULT_TIMEOUT_MILLISECONDS,
                )
                try:
                    page.wait_for_selector(
                        PRODUCT_CARD_SELECTOR,
                        timeout=DEFAULT_TIMEOUT_MILLISECONDS,
                    )
                except PlaywrightTimeoutError:
                    pass

                return page.content()
            finally:
                browser.close()


def _extract_items_from_html(html: str, base_url: str) -> Sequence[WatchItem]:
    """Extract watch items from TK Maxx listing HTML.

    Args:
        html: Raw TK Maxx listing HTML.
        base_url: Base URL used to resolve relative product URLs.

    Returns:
        Normalised watch items extracted from product cards.
    """
    soup = BeautifulSoup(html, "html.parser")
    items: list[WatchItem] = []

    cards = soup.select(PRODUCT_CARD_SELECTOR)

    for index, card in enumerate(cards, start=1):
        if not isinstance(card, Tag):
            continue

        item = _extract_item_from_card(card=card, base_url=base_url, index=index)
        if item is not None:
            items.append(item)

    return items


def _extract_item_from_card(card: Tag, base_url: str, index: int) -> WatchItem | None:
    """Extract a watch item from one TK Maxx product card.

    Args:
        card: Product card HTML element.
        base_url: Base URL used to resolve relative product URLs.
        index: One-based product card index used for debug logging.
    Returns:
        Normalised watch item, or None if the card is incomplete.
    """
    product_link = card.select_one("a.c-product-card[href]")
    if not isinstance(product_link, Tag):
        return None

    href = _get_attribute(product_link, "href")
    if href is None:
        return None

    url = urljoin(base_url, href)
    item_id = _extract_item_id(url)
    if item_id is None:
        return None

    brand = _extract_brand(card)
    product_title = _extract_product_title(card)

    if brand is None:
        return None

    if product_title is None:
        return None

    image_url = _extract_image_url(card=card, base_url=base_url)
    stock_message = _extract_stock_message(card)
    badge = _extract_badge(card)
    card_text = _clean_text(card.get_text(" "))

    return WatchItem(
        source="tkmaxx",
        item_id=item_id,
        title=f"{brand} - {product_title}",
        url=url,
        metadata={
            "brand": brand,
            "product_title": product_title,
            "stock_message": stock_message,
            "price_gbp": _extract_price(card),
            "rrp_gbp": _extract_pattern_float(RRP_PATTERN, card_text),
            "saving_gbp": _extract_pattern_float(SAVING_PATTERN, card_text),
            "saving_percent": _extract_pattern_float(PERCENT_PATTERN, card_text),
            "image_url": image_url,
            "badge": badge,
        },
    )


def _extract_price(card: Tag) -> float | None:
    """Extract the current product price from a product card.

    Args:
        card: Product card HTML element.

    Returns:
        Product price in GBP, or None if unavailable.
    """
    price = _extract_text(card.select_one(".c-product-card__price-val"))
    if price is None:
        return None

    return _parse_gbp(price)


def _extract_brand(card: Tag) -> str | None:
    """Extract the product brand from a product card.

    Args:
        card: Product card HTML element.

    Returns:
        Product brand, or None if unavailable.
    """
    return _extract_text(card.select_one(".c-product-card__text--brand strong"))


def _extract_product_title(card: Tag) -> str | None:
    """Extract the product title from a product card.

    Args:
        card: Product card HTML element.

    Returns:
        Product title, or None if unavailable.
    """
    return _extract_text(card.select_one(".c-product-card__text--label"))


def _extract_stock_message(card: Tag) -> str | None:
    """Extract stock status text from a product card.

    Args:
        card: Product card HTML element.

    Returns:
        Stock status text, or None if unavailable.
    """
    return _extract_text(card.select_one(".c-callout-overlay"))


def _extract_image_url(card: Tag, base_url: str) -> str | None:
    """Extract product image URL from a product card.

    Args:
        card: Product card HTML element.
        base_url: Base URL used to resolve relative image URLs.

    Returns:
        Absolute product image URL, or None if unavailable.
    """
    image = card.select_one("img.c-product-card__thumbnail[src]")
    if not isinstance(image, Tag):
        return None

    src = _get_attribute(image, "src")
    if src is None:
        return None

    return urljoin(base_url, src)


def _extract_badge(card: Tag) -> str | None:
    """Extract product badge text from a product card.

    Args:
        card: Product card HTML element.

    Returns:
        Badge text, or None if unavailable.
    """
    badge = card.select_one("img.c-product-card__badge[alt]")
    if not isinstance(badge, Tag):
        return None

    return _get_attribute(badge, "alt")


def _extract_item_id(url: str) -> str | None:
    """Extract the TK Maxx product ID from a product URL.

    Args:
        url: Absolute or relative TK Maxx product URL.

    Returns:
        Product ID, or None if the URL does not contain one.
    """
    match = PRODUCT_ID_PATTERN.search(url)
    if match is None:
        return None

    return match.group(1)


def _extract_pattern_float(pattern: re.Pattern[str], text: str) -> float | None:
    """Extract a float value from text using a regular expression.

    Args:
        pattern: Compiled regex with the numeric value in group 1.
        text: Text to parse.

    Returns:
        Parsed float, or None if the pattern does not match.
    """
    match = pattern.search(text)
    if match is None:
        return None

    return float(match.group(1).replace(",", ""))


def _parse_gbp(text: str) -> float | None:
    """Parse a GBP value from text.

    Args:
        text: Text containing a pound-denominated value.

    Returns:
        Parsed GBP value, or None if no value is present.
    """
    return _extract_pattern_float(GBP_PATTERN, text)


def _extract_text(element: Tag | None) -> str | None:
    """Extract normalised text from an HTML element.

    Args:
        element: HTML element, or None.

    Returns:
        Clean text, or None if the element has no text.
    """
    if element is None:
        return None

    text = _clean_text(element.get_text(" "))
    if not text:
        return None

    return text


def _get_attribute(element: Tag, attribute: str) -> str | None:
    """Extract a string attribute from an HTML element.

    Args:
        element: HTML element.
        attribute: Attribute name.

    Returns:
        Attribute value, or None if the attribute is missing or non-scalar.
    """
    value = element.get(attribute)
    if not isinstance(value, str):
        return None

    value = _clean_text(value)
    if not value:
        return None

    return value


def _clean_text(text: str) -> str:
    """Normalise whitespace in text.

    Args:
        text: Raw text.

    Returns:
        Text with collapsed whitespace.
    """
    return " ".join(text.split())