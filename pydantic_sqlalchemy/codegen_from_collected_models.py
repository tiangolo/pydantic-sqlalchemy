from pydantic_sqlalchemy.models_collector import ModelsCollector

def ensure_file_module_path(

):

def write_pydantic_models(
        collector: ModelsCollector,
        base_path: str = 'generated',
):
    for ref, model in collector.collected_models.items():
        write_pydantic_model()