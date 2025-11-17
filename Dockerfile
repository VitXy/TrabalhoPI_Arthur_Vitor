# Usa a imagem oficial do PostgreSQL como base
FROM postgres:15

# Define a senha e o banco de dados usando
# Usando variáveis de ambiente
ENV POSTGRES_PASSWORD=california
ENV POSTGRES_DB=jovem
ENV POSTGRES_USER=texas

# Expor a porta padrão do PostgreSQL
EXPOSE 5432acx