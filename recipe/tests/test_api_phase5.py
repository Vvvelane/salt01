from fastapi.testclient import TestClient

from recipe.app import app


def test_research_empty_state_is_real_no_data():
    with TestClient(app) as client:
        response = client.get('/api/v1/research/status')
        assert response.status_code == 200
        payload = response.json()
        assert payload['status'] == 'no_data'
        assert payload['data'] is None
        assert payload['warnings'][0]['code'] == 'research_no_data'
        assert client.get('/api/v1/research/runs').json()['status'] == 'no_data'
        assert client.get('/api/v1/research/runs/missing/pnl').json()['status'] == 'no_data'


def test_research_page_contains_exact_empty_copy():
    with TestClient(app) as client:
        html = client.get('/').text
        script = client.get('/static/js/views/research.js').text
        assert 'No research outputs configured.' in script
        assert 'no_data' in script
        assert 'PnL' in script
