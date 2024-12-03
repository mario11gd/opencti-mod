const express = require('express');
const { spawn } = require('child_process');
const app = express();
const cors = require('cors');

app.use(cors());
const port = 3004;

// Ruta que ejecutará el script Python
app.get('/run-python', (req, res) => {
  print("Conectando con código Python")
  const spawn = require('child_process').spawn

  const pythonProcess = spawn('python', ['script_python.py'])
});

// Iniciar el servidor en el puerto 3004
app.listen(port,"0.0.0.0", () => {
  console.log(`Servidor corriendo en http://138.4.27.55:${port}`);
});
