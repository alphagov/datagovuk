import re
from dataclasses import dataclass
from difflib import get_close_matches
from functools import cache
from pathlib import Path

import frontmatter
from django.conf import settings
from django.urls import reverse
from django.utils.html import strip_tags

from datagovuk.collections.constants import get_collections
from datagovuk.core.markdown import render_markdown

from .constants import STOP_WORDS, TopicChoices
from .solr import get_similar_title_words

MIN_WORD_LENGTH = 3
MIN_PREFIX_LENGTH = 4

# Words too common in page titles to say anything about what a search is looking for
GENERIC_WORDS = {"data", "statistics", "information", "results"}
MAX_SUGGESTIONS = 3
MAX_TERMS_CHECKED = 3
SPELLING_MATCH_CUTOFF = 0.8

# Collection pages are filed under a collection; these say which Topic filter option each belongs to.
# Collections that aren't listed (and pages with no entry) aren't tied to a topic.
COLLECTION_TOPICS = {
    "business-and-economy": TopicChoices.BUSINESS_AND_ECONOMY,
    "environment": TopicChoices.ENVIRONMENT,
    "government": TopicChoices.GOVERNMENT,
    "transport": TopicChoices.TRANSPORT,
}
PAGE_TOPICS = {
    ("land-and-property", "uk-house-prices"): TopicChoices.BUSINESS_AND_ECONOMY,
}


@dataclass(frozen=True)
class CuratedItem:
    title: str
    summary: str
    url: str
    # The words in the title; a search is relevant when it uses a similar word
    keywords: tuple[str, ...]
    # The Topic filter option this item belongs to; None when it isn't tied to a topic
    topic: str | None = None
    # The title of the collection the page is filed under, e.g. "Land and property"
    collection: str = ""


def _words(text):
    return [
        word
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if len(word) >= MIN_WORD_LENGTH and word not in STOP_WORDS
    ]


def _similar(term, word):
    """The same word, or a plural / longer form of it (price and prices, inflation and inflationary)."""
    return term.startswith(word) or (len(term) >= MIN_PREFIX_LENGTH and word.startswith(term))


def _first_paragraph(markdown):
    paragraph = markdown.strip().split("\n\n")[0]
    return " ".join(strip_tags(render_markdown(paragraph)).split())


@cache
def get_all_curated_items():
    """Every published collection page, in the order collections list them."""
    root = Path(settings.DATAGOVUK_CONTENT_COLLECTIONS_ROOT)
    items = []
    for collection in get_collections():
        for page in collection["topics"]:
            path = root / collection["slug"] / f"{page['slug']}.md"
            if not path.exists():
                continue
            with path.open() as page_file:
                parsed = frontmatter.load(page_file)
            if parsed.get("status") != "for-publication":
                continue
            title = parsed.get("title", page["title"])
            topic = PAGE_TOPICS.get((collection["slug"], page["slug"])) or COLLECTION_TOPICS.get(collection["slug"])
            items.append(
                CuratedItem(
                    title=title,
                    summary=_first_paragraph(parsed.content),
                    url=reverse("collections:collection_page", args=[collection["slug"], page["slug"]]),
                    keywords=tuple(word for word in _words(title) if word not in GENERIC_WORDS),
                    topic=topic,
                    collection=collection["title"],
                ),
            )
    return tuple(items)


def _search_terms(query):
    return [term for term in _words(query or "") if term not in GENERIC_WORDS]


def _relevance(item, terms):
    """How many of the search words are about this item."""
    return sum(any(_similar(term, keyword) for keyword in item.keywords) for term in set(terms))


def _allowed_by_topics(item, topics):
    """Ticking topics rules out items that belong to a different topic. Items with no topic are never ruled out."""
    return not topics or not item.topic or item.topic in topics


def get_curated_items(query, topics=(), collections=()):
    """
    The curated items relevant to a search, best match first, or none when the search isn't about any of them.

    Ticking topics narrows this to items in those topics, and ticking collections to pages in those collections.
    On their own (with no search words) they show everything in the ticked topics or collections.
    Items without a topic only ever match on the search words.
    """
    terms = _search_terms(query)
    topics = set(topics or ())
    collections = set(collections or ())

    matches = []
    for item in get_all_curated_items():
        if not _allowed_by_topics(item, topics) or (collections and item.collection not in collections):
            continue
        score = _relevance(item, terms)
        browsing_ticked = not terms and (item.topic in topics or item.collection in collections)
        if score or browsing_ticked:
            matches.append((score, item))
    matches.sort(key=lambda match: -match[0])
    return [item for _, item in matches]


def get_collection_counts(query, topics=()):
    """
    How many curated pages each collection has for a search (every page when there are no search words), so the
    Collection filter can say what ticking each one would show. Collections themselves are not applied.
    """
    terms = _search_terms(query)
    topics = set(topics or ())

    counts = {collection["title"]: 0 for collection in get_collections()}
    for item in get_all_curated_items():
        if _allowed_by_topics(item, topics) and (not terms or _relevance(item, terms)):
            counts[item.collection] += 1
    return counts


def _related_pages(terms):
    """Pages that mention the search words in their text, though not in their title, best match first."""
    scored = []
    for item in get_all_curated_items():
        if _relevance(item, terms):
            continue  # already shown as curated data
        words = _words(item.summary)
        score = sum(any(_similar(term, word) for word in words) for term in set(terms))
        if score:
            scored.append((score, item.title))
    scored.sort(key=lambda match: -match[0])
    return [title for _, title in scored]


def get_suggested_searches(query):
    """
    Searches to try when one found nothing, related to what was searched for, best first:
      1. corrections for words that are close to a word on the site's pages and collections ("inflaton")
      2. corrections for words that are close to a word in dataset titles ("fishry")
      3. the titles of pages whose text mentions the search words
    """
    terms = _search_terms(query)
    vocabulary = {keyword for item in get_all_curated_items() for keyword in item.keywords}
    vocabulary |= {word for collection in get_collections() for word in _words(collection["title"])}
    unknown_terms = [term for term in terms if term not in vocabulary]

    suggestions = []

    def add(suggestion):
        if suggestion not in suggestions:
            suggestions.append(suggestion)

    for term in unknown_terms:
        for match in get_close_matches(term, sorted(vocabulary), n=1, cutoff=SPELLING_MATCH_CUTOFF):
            add(match.capitalize())
    for term in unknown_terms[:MAX_TERMS_CHECKED]:
        for match in get_similar_title_words(term):
            add(match.capitalize())
    for title in _related_pages(terms):
        add(title)
    return suggestions[:MAX_SUGGESTIONS]
