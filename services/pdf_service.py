from pathlib import Path
from datetime import datetime
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)
from reportlab.lib.units import cm


class PDFService:

    def clean_text(self, text: str) -> str:
        text = text.replace("###", "")
        text = text.replace("##", "")
        text = text.replace("#", "")
        text = text.replace("**", "")
        text = text.replace("*", "")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def generate_pdf(self, content: str, output_path: str):

        path = Path(output_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        doc = SimpleDocTemplate(
            str(path),
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        title_style = ParagraphStyle(
            name="Title",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            spaceAfter=20,
        )

        heading_style = ParagraphStyle(
            name="Heading",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            spaceBefore=14,
            spaceAfter=10,
        )

        body_style = ParagraphStyle(
            name="Body",
            fontName="Helvetica",
            fontSize=11,
            leading=18,
            spaceAfter=10,
        )

        story = []

        story.append(
            Paragraph(
                "RELATÓRIO EXECUTIVO IA - PDF CORRIGIDO",
                title_style,
            )
        )

        story.append(
            Paragraph(
                f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                body_style,
            )
        )

        story.append(Spacer(1, 12))

        for line in content.split("\n"):

            line = line.strip()

            if not line:
                story.append(Spacer(1, 8))
                continue

            line = self.clean_text(line)

            if (
                "Resumo Executivo" in line
                or "Melhor Setor" in line
                or "Pior Setor" in line
                or "Insights Estratégicos" in line
                or "Recomendações Empresariais" in line
            ):

                story.append(
                    Paragraph(line, heading_style)
                )

            else:

                story.append(
                    Paragraph(line, body_style)
                )

        doc.build(story)

        return str(path)