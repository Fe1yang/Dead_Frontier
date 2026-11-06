from agent_gw import AgentGwClient

queries = ['realistic pistol GLB game asset', 'compact SMG GLB game asset', 'pump shotgun GLB game asset', 'sniper rifle GLB game asset']
with AgentGwClient() as client:
    for query in queries:
        result = client.tools.search_design_asset(query, top_k=4, type='3d').json()
        print('\nQUERY', query)
        for item in result.get('results', []):
            print({k: item.get(k) for k in ('uuid', 'name', 'title', 'description', 'license', 'formats')})
