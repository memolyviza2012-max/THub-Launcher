
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Core')))
from trun_app import TRunWorker

cfg = {}
profile = {}
in_csv = 'dummy_in.csv'
out_csv = 'dummy_out.csv'

try:
    worker = TRunWorker(
        config=cfg,
        profile=profile,
        input_csv=in_csv,
        output_csv=out_csv,
        batch_size=20,
        delay_ms=0,
        max_retries=3,
        use_mask=False,
        use_glossary=False,
        use_pua=False,
        peak_config=None,
        threads=1,
        token_burner=False
    )
    print('Worker instantiated successfully.')
except Exception as e:
    print('Failed to instantiate worker:', type(e), e)
    traceback.print_exc()
