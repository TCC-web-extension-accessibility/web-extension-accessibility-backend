import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class VoiceCommand:
    intent: str
    action: str
    target: Optional[str] = None
    value: Optional[str] = None
    confidence: float = 0.0

class NLUService:
    def __init__(self):
        self.command_patterns = self._initialize_patterns()
        self.element_selectors = self._initialize_selectors()
    
    def _initialize_patterns(self) -> Dict[str, List[Tuple[str, float]]]:
        """Inicializa padrões de reconhecimento de comandos em português"""
        return {
            "navegar": [
                (r"(?:ir para|navegar para|mover para|descer para|subir para)\s+(?:o\s+)?(.+)", 0.9),
                (r"(?:rolar|scroll)\s+(?:para\s+)?(?:baixo|cima|esquerda|direita)", 0.8),
                (r"(?:próximo|anterior)\s+(?:elemento|item|link|botão)", 0.8),
                (r"(?:primeiro|último)\s+(?:elemento|item|link|botão)", 0.8),
            ],
            "clicar": [
                (r"(?:clicar|clique|pressionar|ativar|selecionar)\s+(?:em|no|na)\s+(.+)", 0.9),
                (r"(?:botão|link|elemento)\s+(.+)", 0.7),
                (r"(?:número|índice)\s+(\d+)", 0.8),
            ],
            "ler": [
                (r"(?:ler|lê|dizer|falar)\s+(?:o\s+)?(.+)", 0.9),
                (r"(?:o que é|que é|descrever)\s+(.+)", 0.8),
                (r"(?:ler|lê)\s+(?:página|conteúdo|texto)", 0.8),
            ],
            "ajuda": [
                (r"(?:ajuda|comandos|o que posso dizer|instruções)", 0.9),
                (r"(?:como usar|como funciona|tutorial)", 0.8),
            ],
            "voltar": [
                (r"(?:voltar|retroceder|página anterior)", 0.9),
                (r"(?:fechar|sair|cancelar)", 0.8),
            ],
            "zoom": [
                (r"(?:aumentar|diminuir)\s+(?:zoom|tamanho|fonte)", 0.8),
                (r"(?:maior|menor)\s+(?:texto|fonte)", 0.7),
            ]
        }
    
    def _initialize_selectors(self) -> Dict[str, str]:
        """Inicializa seletores para elementos acessíveis"""
        return {
            "botão": "button, [role='button'], input[type='button'], input[type='submit']",
            "link": "a[href], [role='link']",
            "campo": "input, textarea, select, [role='textbox'], [role='combobox']",
            "cabeçalho": "h1, h2, h3, h4, h5, h6, [role='heading']",
            "lista": "ul, ol, [role='list']",
            "item_lista": "li, [role='listitem']",
            "tabela": "table, [role='table']",
            "navegação": "nav, [role='navigation']",
            "main": "main, [role='main']",
            "complementar": "aside, [role='complementary']",
            "banner": "header, [role='banner']",
            "rodapé": "footer, [role='contentinfo']"
        }
    
    def process_command(self, text: str) -> VoiceCommand:
        """
        Processa um comando de voz e retorna a intenção mapeada
        
        Args:
            text: Texto transcrito do comando de voz
            
        Returns:
            VoiceCommand com intenção e ação mapeadas
        """
        text = text.lower().strip()
        
        # Procura por padrões de comando
        best_match = None
        highest_confidence = 0.0
        
        for intent, patterns in self.command_patterns.items():
            for pattern, base_confidence in patterns:
                match = re.search(pattern, text)
                if match:
                    confidence = base_confidence
                    
                    # Ajusta confiança baseado no comprimento do texto
                    if len(text) > 20:
                        confidence *= 0.9
                    elif len(text) < 10:
                        confidence *= 1.1
                    
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        best_match = (intent, pattern, match, confidence)
        
        if best_match:
            intent, pattern, match, confidence = best_match
            groups = match.groups()
            
            if intent == "navegar":
                if "rolar" in text or "scroll" in text:
                    if "baixo" in text:
                        action = "scroll_down"
                    elif "cima" in text:
                        action = "scroll_up"
                    elif "esquerda" in text:
                        action = "scroll_left"
                    elif "direita" in text:
                        action = "scroll_right"
                    else:
                        action = "scroll_down"
                    target = None
                elif "próximo" in text or "anterior" in text:
                    action = "navigate_next" if "próximo" in text else "navigate_previous"
                    target = None
                else:
                    action = "navigate_to"
                    target = groups[0] if groups else None
                    
            elif intent == "clicar":
                action = "click"
                if groups:
                    target = groups[0]
                elif "número" in text or "índice" in text:
                    # Extrai número do comando
                    num_match = re.search(r'(\d+)', text)
                    target = f"index_{num_match.group(1)}" if num_match else None
                else:
                    target = None
                    
            elif intent == "ler":
                action = "read"
                target = groups[0] if groups else "page_content"
                
            elif intent == "ajuda":
                action = "show_help"
                target = None
                
            elif intent == "voltar":
                action = "go_back"
                target = None
                
            elif intent == "zoom":
                action = "zoom_in" if "aumentar" in text or "maior" in text else "zoom_out"
                target = None
                
            else:
                action = intent
                target = groups[0] if groups else None
            
            return VoiceCommand(
                intent=intent,
                action=action,
                target=target,
                confidence=confidence
            )
        
        # Comando não reconhecido
        return VoiceCommand(
            intent="unknown",
            action="unknown",
            confidence=0.0
        )
    
    def get_element_selector(self, element_type: str) -> str:
        """Retorna o seletor CSS para um tipo de elemento"""
        return self.element_selectors.get(element_type, "*")
    
    def get_all_selectors(self) -> Dict[str, str]:
        """Retorna todos os seletores disponíveis"""
        return self.element_selectors.copy() 