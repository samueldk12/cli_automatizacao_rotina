"""Journalism Department Plugin - Editorial planning, fact-checking, news writing and editing."""

NAME = "Journalism"
DESCRIPTION = "Manages editorial content, fact-checking, news reporting and editorial board decisions."
SPECIALISTS = ["pauta_journal", "fact_checker", "redacao_news", "editorial"]
MIDDLEWARES: list[str] = []
PARENT_COMPANY = None
ROLE = "You are a journalism department responsible for editorial planning, rigorous fact-checking, news writing and editorial oversight. Produce accurate, well-sourced reporting while maintaining journalistic ethics, editorial standards and timely delivery across all content channels."
