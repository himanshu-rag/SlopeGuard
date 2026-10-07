with open('main.py', 'r') as f:
    content = f.read()

if 'CORSMiddleware' not in content:
    content = content.replace('app = FastAPI()', "from fastapi.middleware.cors import CORSMiddleware\n\napp = FastAPI()\n\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=['*'],\n    allow_credentials=True,\n    allow_methods=['*'],\n    allow_headers=['*'],\n)\n")
    with open('main.py', 'w') as f:
        f.write(content)
