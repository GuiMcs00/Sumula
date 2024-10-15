# Súmula

## Busca de Artigos

O **Súmula** é um robô desenvolvido para buscar artigos publicados no *Diário Oficial da União* (D.O.U.) de acordo com critérios definidos por uma lista no SharePoint. Essa lista especifica escopos e termos que devem estar presentes nos artigos, além de permitir a exclusão de termos indesejados. 
Dessa forma, o **Súmula** garante uma busca precisa, identificando apenas os artigos de real interesse.

## Objetivo do Projeto

O **Projeto Súmula** foi desenvolvido para atender às necessidades do Banco Central do Brasil (BCB), automatizando a leitura diária do D.O.U. e mantendo os departamentos informados sobre as publicações relevantes para o órgão. A ferramenta facilita o acompanhamento de novas regulamentações, 
notícias e outros conteúdos de interesse do BCB.

## Funcionalidades Extras

Além da busca de artigos, o **Súmula** oferece funcionalidades adicionais, como o armazenamento dos arquivos XML de publicações do *Inlabs* e a coleta de todos os artigos que atendem aos critérios definidos. Essas funcionalidades complementares ampliam o valor da solução para o Banco Central, 
centralizando e organizando dados críticos de forma automatizada.

---

## Minha Contribuição no Projeto Súmula

Quando entrei na organização, o **Súmula** já estava em produção, mas apresentava diversas falhas. O código original era mal otimizado e implementado, com critérios de busca confusos e especificações distribuídas entre uma lista pouco intuitiva no SharePoint e hardcode diretamente no sistema.

Identifiquei e corrigi esses problemas, reformulando a **arquitetura do projeto** e **otimizando significativamente** o desempenho da busca. Vou explicar com detalhes as principais melhorias que implementei:

- **Redesenho da solução de busca**: Transformei a busca de artigos em um processo mais rápido, organizado e preciso, eliminando a redundância e confusão do código original.
- **Flexibilização dos critérios de busca**: Desenvolvi uma nova forma de especificar critérios, permitindo a combinação de múltiplos termos, definição do escopo de busca, uso de expressões regulares (regex) para variações, e a inclusão de exceções específicas para cada critério.
- **Centralização das especificações**: Unifiquei a configuração dos critérios de busca, retirando-os do hardcode e migrando tudo para uma interface mais intuitiva e acessível via SharePoint.
- **Otimização da arquitetura**: Melhorei a organização do código, aumentando a legibilidade, manutenção futura e a reutilizabilidade de funções, além de garantir escalabilidade para atender às necessidades do Banco Central.

Praticamente reestruturei o projeto desde o início, aproveitando pouco do código original, devido à sua baixa qualidade e falta de organização.
