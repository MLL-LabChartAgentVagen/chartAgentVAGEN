project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from chartGenerators.bar_chart.bar_chart_generator import BarChartGenerator