## 📌 Padrão de Projeto Utilizado: Facade
Para simplificar a interação com a lógica de negócios, implementamos o padrão **Facade**, centralizando operações complexas em uma única classe (`TriagemService`).

### **✅ Benefícios do Facade no PEWS-Teste**
- **Código mais limpo e organizado** 🧹
- **Desacoplamento entre views e modelos** 🚀
- **Facilidade para manutenção e testes** ✅

### **📌 Exemplo de Uso**
```python
from triagem.services import TriagemService

# Criando um novo paciente
paciente = TriagemService.cadastrar_paciente("Ana Souza", 6, "102A", "D789", "Pneumonia")

# Registrando uma avaliação
avaliacao = TriagemService.registrar_avaliacao(paciente.id, 6, 110, 28, "Paciente estável", "Alerta", "Pressão normal", "Respiração normal", "Nenhum")
