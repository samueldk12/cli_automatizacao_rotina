# CARTA DE COMUNICAÇÃO DE INCIDENTE DE SEGURANÇA

**Comunicação Obrigatória — Lei nº 13.709/2018 (LGPD) — Art. 44 e 48**

---

**Data:** 2 de julho de 2024

**Remetente:**

> **Startup Exemplo Tecnologia S.A.**

> CNPJ: 00.000.000/0001-00

> Endereço: Av. Brigadeiro Faria Lima, 0000 — São Paulo/SP — CEP 00000-000

> E-mail do Encarregado (DPO): dpo@startup-exemplo.com.br

> Telefone: (11) 3000-0000

**Destinatário:**

> Cliente/Cadastrado(a) — Titular dos Dados Pessoais

---

## 1. OBJETO

Prezado(a) Senhor(a),

A **Startup Exemplo Tecnologia S.A.**, na qualidade de controladora dos seus dados pessoais, nos termos da Lei Geral de Proteção de Dados — **LGPD (Lei nº 13.709/2018)**, vem, por meio desta, comunicar incidente de segurança que envolveu seus dados pessoais, em cumprimento ao disposto nos **Artigos 44 e 48** da referida legislação.

## 2. DESCRICAO DO INCIDENTE

Em **15 de junho de 2024**, nossa equipe de segurança foi notificada, por meio de um programa de recompensa (bug bounty) operado pela empresa **Bounty Company**, sobre a existência de uma vulnerabilidade de segurança em nossa aplicação web.

**Detalhes técnicos do incidente:**

| Campo | Informação |
|-------|-----------|
| Identificador | CVE-2024-1234 |
| Tipo de vulnerabilidade | SQL Injection (Injeção SQL) — CWE-89 |
| Componente afetado | Endpoint de autenticação: `/api/v1/auth/login` |
| Severidade CVSS 3.1 | **9.8 — Crítica** |
| Data de descoberta | 15/06/2024 |
| Data de correção | 28/06/2024 |

A vulnerabilidade permitia que um agente mal-intencionado, sem necessidade de autenticação, inserisse comandos SQL maliciosos no formulário de login da aplicação, o que poderia resultar em:

- **(a)** Bypass de autenticação — acesso não autorizado a contas de usuários;
- **(b)** Extração de dados do banco de dados — incluindo nome de usuário, e-mail, hash de senha e CPF parcial;
- **(c)** Escalação de privilégios — acesso a funcionalidades administrativas.

## 3. DADOS AFETADOS

Com base na investigação forense realizada, confirmamos que os seguintes dados pessoais podem ter sido acessados indevidamente:

- ✅ Nome de usuário (username)
- ✅ Endereço de e-mail
- ✅ Hash de senha (criptografado com BCrypt)
- ✅ CPF parcial (formato `000.000.000-XX`)
- ❌ Número completo de cartão de crédito — **NÃO foi acessado**
- ❌ Senhas em texto claro — **NÃO foram expostas** (armazenadas com BCrypt)
- ❌ Documentos de identidade completos — **NÃO foram acessados**

**Importante esclarecer:** As senhas estavam protegidas com o algoritmo **BCrypt**, o que significa que, mesmo que os hashes tenham sido extraídos, eles são computacionalmente inviáveis de serem revertidos em um tempo prático, devido ao fator de custo do BCrypt.

## 4. ADOCOES TOMADAS

Informamos que, tão logo tivemos ciência do incidente, adotamos as seguintes medidas:

| Data | Ação |
|------|------|
| 15/06/2024 | Confirmação da vulnerabilidade e início da investigação |
| 15/06/2024 | WAF configurado com regras emergenciais de proteção contra SQL Injection |
| 16/06/2024 | Notificação à ANPD (Autoridade Nacional de Proteção de Dados) |
| 17/06/2024 | Contratação da empresa **Bounty Company** para pentest completo |
| 20/06/2024 | Desenvolvimento das correções no código-fonte |
| 25/06/2024 | Deploy das correções em ambiente de staging para validação |
| 28/06/2024 | Deploy das correções em produção (atualização sem interrupção) |
| 28/06/2024 | Revisão e rotação de todas as credenciais de banco de dados |
| 01/07/2024 | Teste de regressão de segurança — sem resquícios da vulnerabilidade |
| 02/07/2024 | Emissão desta carta de comunicação a todos os titulares afetados |

## 5. SEU DIREITO COMO TITULAR

Em conformidade com a LGPD, informamos que você, como titular dos dados pessoais, possui os seguintes direitos (Art. 18):

- **Direito de confirmação e acesso** — solicitar confirmação do tratamento e acessar seus dados;
- **Direito de retificação** — solicitar correção de dados incompletos, inexatos ou desatualizados;
- **Direito à eliminação** — solicitar a exclusão de dados tratados com base no seu consentimento;
- **Direito à portabilidade** — solicitar a transferência de seus dados a outro fornecedor de serviço;
- **Direito de revogação do consentimento** — a qualquer momento, mediante manifestação expressa;
- **Direito de reclamação perante a ANPD** — a qualquer momento, no site **www.gov.br/anpd**.

## 6. MEDIDAS QUE RECOMENDAMOS ADOTAR

Para sua segurança, recomendamos as seguintes ações:

1. **Alterar sua senha** imediatamente em nossa plataforma;
2. **Não utilizar a mesma senha** em outros serviços ou aplicações;
3. **Ativar autenticação de dois fatores (2FA)** em nossa plataforma (agora disponível em Configurações > Segurança);
4. **Monitorar suas contas** financeiras e e-mails por atividades suspeitas;
5. **Nunca compartilhar** senhas, códigos de verificação ou dados pessoais por e-mail ou telefone.

## 7. CANAL DE CONTATO

Para quaisquer dúvidas, reclamações ou exercício de seus direitos, entre em contato com nosso Encarregado de Proteção de Dados (DPO):

- **E-mail:** dpo@startup-exemplo.com.br
- **Telefone:** (11) 3000-0000 (opção 4)
- **Endereço:** Av. Brigadeiro Faria Lima, 0000, 10º andar — São Paulo/SP — CEP 00000-000
- **Horário de atendimento:** Segunda a sexta, das 9h às 18h

## 8. BASE LEGAL

A presente comunicação é realizada em conformidade com:

- **Art. 44 da LGPD:** "Os agentes de tratamento devem adotar medidas de segurança, técnicas e administrativas aptas a proteger os dados pessoais de acessos não autorizados";
- **Art. 48 da LGPD:** "O controlador deve comunicar à autoridade nacional e ao titular a ocorrência de incidente de segurança";
- **Art. 6º, inciso X, alínea "c" da LGPD:** Princípio da prevenção;
- **Orientação 01/2024 da ANPD** sobre comunicação de incidentes de segurança.

---

### ASSINATURA

**Startup Exemplo Tecnologia S.A.**

Controladora dos Dados Pessoais

Responsável: ______________________

Cargo: Diretor(a) de Tecnologia (CTO)

Data: 02/07/2024

---

### ANEXOS (referência)

- Anexo A: Relatório Técnico Completo — CVE-2024-1234 (Bounty Company)
- Anexo B: Guia de Redefinição de Senha
- Anexo C: Perguntas Frequentes (FAQ)

---

*> Esta comunicação é sigilosa e destina-se exclusivamente ao destinatário. A reprodução total ou parcial sem autorização é vedada, nos termos do Art. 153 do Código Penal Brasileiro (revelação de segredo) e do Art. 46 da LGPD.*
