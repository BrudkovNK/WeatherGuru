import weather_parser as wp
import risk_calculator as rc
import traceback as tb
import sys

try:
    wp.main()
except Exception as e:
    print(f"Парсер сломался из-за: {e}")
    tb.print_exc()
    sys.exit(1)

try:
    rc.main()
except Exception as e:
    print(f"Калькулятор сломался из-за: {e}")
    tb.print_exc()
    sys.exit(1)