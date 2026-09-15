from backend.schemas.document_schema import StructuredDocument


class DocumentEvaluator:
    """Evaluate the completeness of structured document extraction."""

    def evaluate(self, document: StructuredDocument) -> dict:
        """Return basic quality metrics for an extracted document."""

        if not isinstance(document, StructuredDocument):
            raise TypeError("document must be a StructuredDocument")

        metadata_fields = {
            "document_title": document.metadata.document_title,
            "authors": document.metadata.authors,
            "organizations": document.metadata.organizations,
        }

        content_fields = {
            "research_topic": document.content.research_topic,
            "objective": document.content.objective,
            "dataset_information": document.content.dataset_information,
            "methodology": document.content.methodology,
            "algorithms_or_models": document.content.algorithms_or_models,
            "experimental_setup": document.content.experimental_setup,
            "results_and_metrics": document.content.results_and_metrics,
            "key_findings": document.content.key_findings,
            "conclusions": document.content.conclusions,
            "important_dates": document.content.important_dates,
            "technical_terms": document.content.technical_terms,
            "observations": document.content.observations,
        }

        metadata_filled = sum(
            self._is_filled(value)
            for value in metadata_fields.values()
        )

        content_filled = sum(
            self._is_filled(value)
            for value in content_fields.values()
        )

        total_fields = len(metadata_fields) + len(content_fields)
        filled_fields = metadata_filled + content_filled

        completeness_percentage = (
            filled_fields / total_fields
        ) * 100

        return {
            "file_name": document.metadata.file_name,
            "metadata_filled": metadata_filled,
            "metadata_total": len(metadata_fields),
            "content_filled": content_filled,
            "content_total": len(content_fields),
            "filled_fields": filled_fields,
            "total_fields": total_fields,
            "completeness_percentage": round(
                completeness_percentage, 2
            ),
        }

    @staticmethod
    def _is_filled(value) -> bool:
        """Check whether a field contains meaningful extracted data."""

        if value is None:
            return False

        if isinstance(value, str):
            return bool(value.strip())

        if isinstance(value, list):
            return len(value) > 0

        if isinstance(value, dict):
            return len(value) > 0


        return True