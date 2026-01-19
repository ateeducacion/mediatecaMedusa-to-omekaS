# Primero ver cuáles tienen problemas
find . -type f -exec perl -l -ne 'print $ARGV and close ARGV if /[\x00-\x08\x0B\x0C\x0E-\x1F]/' {} + > archivos_problematicos.txt

# Luego limpiar solo esos
cat archivos_problematicos.txt | xargs perl -i.bak -pe 's/[\x00-\x08\x0B\x0C\x0E-\x1F]//g'