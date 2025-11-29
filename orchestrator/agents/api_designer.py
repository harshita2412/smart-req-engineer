import json
from typing import Dict

def design_api(parsed: Dict):
    """
    Create a small OpenAPI-like dict describing a primary resource based on actions.
    This is intentionally minimal for demo/evaluation purposes.
    """
    title = "resource"
    if parsed.get('actions'):
        title = parsed['actions'][0]['action'] + "_resource"
    api = {
        "openapi": "3.0.0",
        "info": {"title": "Generated API", "version": "0.1"},
        "paths": {}
    }
    # create a single endpoint for create/read/delete if present
    if any(a['action']=='create' for a in parsed.get('actions',[])):
        api['paths']['/items'] = {
            "post": {"description": "Create item", "responses": {"201": {"description": "Created"}}}
        }
    if any(a['action']=='read' for a in parsed.get('actions',[])):
        api['paths'].setdefault('/items',{})["get"] = {"description":"List items","responses":{"200":{"description":"OK"}}}
    if any(a['action']=='delete' for a in parsed.get('actions',[])):
        api['paths'].setdefault('/items',{})["delete"] = {"description":"Delete item","responses":{"204":{"description":"No Content"}}}
    return api
