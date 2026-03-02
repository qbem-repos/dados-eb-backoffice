class ValidateEnvMixin:
    """Mixin que fornece validação de variáveis de ambiente."""
    
    @classmethod
    def validate_all_env_vars(cls, raise_exception: bool = True) -> dict:
        """
        Verifica se todas as variáveis de ambiente estão preenchidas (não-None).
        
        Args:
            raise_exception: Se True, levanta exceção ao encontrar None. Se False, retorna dict com erros.
            
        Returns:
            dict: Dicionário com variáveis None encontradas (vazio se todas OK)
            
        Raises:
            ValueError: Se raise_exception=True e houver variáveis com valor None
        """
        missing_vars = {}
        
        # Percorre todos os atributos da classe
        for attr_name in dir(cls):
            # Ignora métodos privados e especiais
            if attr_name.startswith('_'):
                continue
                
            attr = getattr(cls, attr_name)
            
            # Se é uma classe interna (nested class), verifica recursivamente
            if isinstance(attr, type):
                for nested_attr_name in dir(attr):
                    if nested_attr_name.startswith('_'):
                        continue
                    
                    nested_attr = getattr(attr, nested_attr_name)
                    
                    # Ignora métodos e classes
                    if callable(nested_attr) or isinstance(nested_attr, type):
                        continue
                    
                    # Verifica se o valor é None
                    if nested_attr is None:
                        missing_vars[f"{attr_name}.{nested_attr_name}"] = None
            
            # Se é um atributo direto (não método nem classe)
            elif not callable(attr):
                if attr is None:
                    missing_vars[attr_name] = None
        
        # Se houver variáveis faltando e deve levantar exceção
        if missing_vars and raise_exception:
            missing_list = ', '.join(missing_vars.keys())
            raise ValueError(
                f"The following environment variables are missing (None): {missing_list}"
            )
        
        return missing_vars
