from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Exporta todos os dados do banco para um arquivo JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            "-o",
            help="Caminho do arquivo de sa\u00edda. Padrao: dump_<timestamp>.json",
        )

    def handle(self, *args, **options):
        output = options.get("output")
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = f"dump_{timestamp}.json"

        out_path = Path(output)
        with open(out_path, "w", encoding="utf-8") as f:
            call_command("dumpdata", stdout=f, indent=2)

        self.stdout.write(self.style.SUCCESS(f"Dump gerado em {out_path.resolve()}"))

