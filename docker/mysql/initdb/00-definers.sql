-- Los dumps traen triggers con DEFINER=`integration_user`@`%`.
-- Creamos el rol para que el import no emita warnings de definer inexistente.
CREATE USER IF NOT EXISTS 'integration_user'@'%' IDENTIFIED BY 'integration_user';
GRANT ALL PRIVILEGES ON integration.* TO 'integration_user'@'%';
FLUSH PRIVILEGES;
