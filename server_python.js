const express = require('express');
const { spawn } = require('child_process');
const app = express();
const cors = require('cors');

app.use(cors());
const port = 3005;

// Ruta que ejecutará el script Python
app.get('/prueba', (req, res) => {
  console.log("Conectando con código Python")
  const pythonProcess = spawn('python3', ['prueba.py'])

  let output = '';
  pythonProcess.stdout.on('data', (data) => {
    output += data.toString(); 
    console.log(output)
  });
});

app.get('/import', (req, res) => {
  console.log("Conectando con código Python")
  const pythonProcess = spawn('python3', ['import_data.py'])

  let output = '';
  pythonProcess.stdout.on('data', (data) => {
    output += data.toString(); 
    console.log(output)
  });
});

// Iniciar el servidor en el puerto 3005
app.listen(port,"0.0.0.0", () => {
  console.log(`Servidor corriendo en http://138.4.27.55:${port}`);
});
