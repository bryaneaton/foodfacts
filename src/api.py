"""API client for OpenFoodFacts product data retrieval.

This module provides functionality to interact with the OpenFoodFacts API,
including pagination, rate limiting, and error handling.
"""

import logging
from time import sleep
from typing import Iterator

import niquests as niq
from niquests import Response

logger = logging.getLogger(__name__)


class OpenFoodFactsAPI:
    """API client for OpenFoodFacts"""

    def __init__(self, base_url: str = "https://world.openfoodfacts.org/cgi/search.pl"):
        self.base_url = base_url
        self.headers = {"User-Agent": "fetch-openfoodfacts/0.1 (your@email.com)"}
        self.page_size = 250
        self.rate_limit_delay = 0.6  # 100/min = 1 every 0.6s
        self.max_retries = 3
        self.base_backoff_delay = 1.0  # Base delay in seconds
        self.max_backoff_delay = 60.0  # Max delay in seconds

    def _make_request_with_retry(self, url: str, params: dict = None) -> Response:
        """Make HTTP request with retry and exponential backoff"""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                response = niq.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                return response
            except (niq.RequestException, niq.HTTPStatusError) as e:
                last_exception = e

                if attempt == self.max_retries:
                    logger.error(
                        "Request failed after %d attempts: %s", self.max_retries + 1, e
                    )
                    break

                # Calculate exponential backoff with jitter
                backoff_delay = min(
                    self.base_backoff_delay * (2**attempt), self.max_backoff_delay
                )
                delay = backoff_delay

                logger.debug(
                    "Backoff calculation: attempt=%d, base_delay=%.2fs, backoff_delay=%.2fs, final_delay=%.2fs",
                    attempt,
                    self.base_backoff_delay,
                    backoff_delay,
                    delay,
                )
                logger.warning(
                    "Request failed (attempt %d/%d): %s. Retrying in %.2fs",
                    attempt + 1,
                    self.max_retries + 1,
                    e,
                    delay,
                )
                sleep(delay)

        if last_exception:
            raise last_exception

    def get_total_count(self, response: Response) -> int:
        """Get total count of products for given search parameters"""
        try:
            response.raise_for_status()
            data = response.json()
            return data["count"]
        except (niq.RequestException, KeyError, ValueError) as e:
            logger.error("Error getting total product count: %s", e)
            return 0

    def paginate_products(
        self, params: dict, max_pages: int = None
    ) -> tuple[Iterator[dict], int]:
        """Returns iterator of products and total count"""
        logger.info("Starting product pagination with params: %s", params)
        if max_pages:
            logger.debug("Max pages limit set to: %d", max_pages)

        # Get total count from first request
        initial_params = params.copy()
        initial_params["page"] = 1
        initial_params["page_size"] = self.page_size

        try:
            initial_response = self._make_request_with_retry(
                self.base_url, params=initial_params
            )
            total_count = self.get_total_count(initial_response)
        except (niq.RequestException, ValueError) as e:
            logger.error("Error getting initial product count: %s", e)
            return iter([]), 0

        logger.info("Found %d total products to fetch", total_count)

        def product_iterator():
            page = 1
            total_products_yielded = 0
            first_page_data = initial_response.json()  # Reuse initial response

            while True:
                logger.debug(
                    "Processing page %d with %d items per page", page, self.page_size
                )

                try:
                    # Use cached first page data, otherwise make API call
                    if page == 1:
                        data = first_page_data
                        page_products = data["products"]
                    else:
                        # Add pagination parameters for subsequent pages
                        current_params = params.copy()
                        current_params["page"] = page
                        current_params["page_size"] = self.page_size

                        response = self._make_request_with_retry(
                            self.base_url, params=current_params
                        )
                        data = response.json()
                        page_products = data["products"]

                    # Yield each product individually
                    for product in page_products:
                        yield product
                        total_products_yielded += 1

                    logger.debug(
                        "Page %d: Retrieved %d products. Total yielded: %d/%d",
                        page,
                        len(page_products),
                        total_products_yielded,
                        total_count,
                    )

                except (niq.RequestException, KeyError, ValueError) as e:
                    logger.error("Error fetching page %d: %s", page, e)
                    break

                # Check if we've processed all products on this page
                if len(page_products) == 0:
                    logger.debug("No more products to fetch - empty page")
                    break

                # Check if we've hit our max page limit
                if max_pages and page >= max_pages:
                    logger.warning("Reached max page limit: %d", max_pages)
                    break

                page += 1
                logger.debug(
                    "Waiting %ss before next request (rate limit compliance)",
                    self.rate_limit_delay,
                )
                sleep(self.rate_limit_delay)

            logger.debug(
                "Pagination complete. Total products yielded: %d",
                total_products_yielded,
            )

        return product_iterator(), total_count


# Convenience function for backward compatibility
def paginate_products(
    base_url: str, params: dict, max_pages: int = None
) -> tuple[Iterator[dict], int]:
    """Convenience function that uses OpenFoodFactsAPI class"""
    api = OpenFoodFactsAPI(base_url)
    return api.paginate_products(params, max_pages)
