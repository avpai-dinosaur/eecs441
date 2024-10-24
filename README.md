# eecs441

## Frontend

To run the front end

```
cd frontend
python3 -m http.server
```

and navigate to localhost:8000 (or whatever default port was given) in your browser.

## Backend

To run the back end

```
cd backend
pip install -r requirements.txt
python3 data.py
```

### Register

```
curl -X POST http://localhost:5000/register -H "Content-Type: application/json" -d '{"username": "your_username"}'
```

### Common Questions

```
curl -X POST http://localhost:5000/common-questions -H "Content-Type: application/json" -d '{"username": "your_username"}'
```

### Update Companies

```
curl -X POST http://localhost:5000/update-companies -H "Content-Type: application/json" -d '{"username": "ashvin", "companies": ["microsoft", "oracle", ...]}'
```

### Get Companies
```
curl -X POST http://localhost:5000/get-companies -H "Content-Type: application/json" -d '{"username": "ashvin"}'
```