import importlib.util, sys, unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "research" / "capital_matrix" / "build_v31_three_month_population.py"
spec = importlib.util.spec_from_file_location("population_builder", SCRIPT)
builder = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = builder
spec.loader.exec_module(builder)

class GapSegmentationTests(unittest.TestCase):
    def test_splits_at_any_missing_minute_and_preserves_rows(self):
        bars = [{"time":t} for t in (60,120,180,600,660,900)]
        segments,gaps = builder.split_segments(bars)
        self.assertEqual([len(x) for x in segments],[3,2,1])
        self.assertEqual(len(gaps),2)
        self.assertEqual([g["missing_minute_slots"] for g in gaps],[6,3])
        self.assertEqual(sum(map(len,segments)),len(bars))

    def test_contiguous_data_is_one_segment(self):
        bars = [{"time":t} for t in (60,120,180,240)]
        segments,gaps = builder.split_segments(bars)
        self.assertEqual(len(segments),1)
        self.assertEqual(gaps,[])

if __name__=="__main__": unittest.main()
