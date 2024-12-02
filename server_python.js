const express = require('express');
const { spawn } = require('child_process');
const app = express();
const port = 3004;

// Ruta que ejecutará el script Python
app.get('/run-python', (req, res) => {
  // Ejecutamos el archivo Python 'prueba.py' (asegúrate de que esté en la misma carpeta o especifica la ruta completa)
  const pythonProcess = spawn('python3', ['prueba.py']);
  let pythonResponse = '';

  // Capturamos la salida de stdout de Python
  pythonProcess.stdout.on('data', (data) => {
    pythonResponse += data.toString();
  });

  // Cuando Python termine de ejecutarse, enviamos la respuesta al cliente
  pythonProcess.stdout.on('end', () => {
    res.send(pythonResponse);  // Enviar la respuesta al navegador
  });

  // Enviar un dato al script Python, si es necesario
  pythonProcess.stdin.write('backendi');
  pythonProcess.stdin.end();  // Terminar la entrada al script Python
});

// Iniciar el servidor en el puerto 3004
app.listen(port,"0.0.0.0", () => {
  console.log(`Servidor corriendo en http://138.4.27.55:${port}`);
});
