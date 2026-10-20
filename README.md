--> Pré Requisitos:

    Python 3.12

    Instalação das bibliotecas necessárias via terminal:

    pip install dash dash-leaflet osmnx networkx shapely
    pip install scipy

--> Como executar?

    Abra o terminal na pasta principal do projeto (TP1---ALG-2).

    Execute o comando:

    python app.py

    Abra o navegador no endereço padrão http que surgir indicado.

--> Como se usa?

    1) Página Inicial:

        Digite a quantidade de entregadores a serem gerados (valor numérico).

        Digite o nome (ou prefixo) do bar e/ou o endereço.

        Informe o raio da busca em metros.

        Clique no botão "Enviar!".

       2) Resultados:

        - Mapa Interativo: exibe pinos coloridos para os estabelecimentos encontrados, círculos com a cor correspondente para os entregadores dentro do raio e marcadores agrupados para os que estão fora do raio.

        - Tabela Dinâmica: lista detalhada com o nome do bar, id do entregador, distância real percorrida pelas ruas de Belo Horizonte (em metros) e o tempo de chegada.

--> Observações: 

    No desenvolvimento do trabalho foi utilizado o sistema operacional Windows tanto para construção, como para testes. 
    Além disso, o tempo de execução do algoritmo depende do tamanho dos parâmetros informados pelo o usuário. Dependendo da magnitude desses parâmetros, o processamento pode levar mais tempo para ser concluído e apresentar os resultados
