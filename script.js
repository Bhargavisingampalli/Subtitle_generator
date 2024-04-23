const translations = {
    english: {
      processing: 'Processing uploaded file for English language...',
      completed: 'Subtitle generation completed. Here is the converted text in English:'
    },
    spanish: {
      processing: 'Procesando archivo cargado para el idioma español...',
      completed: 'Generación de subtítulos completada. Aquí está el texto convertido en español:'
    },
    french: {
      processing: 'Traitement du fichier chargé pour la langue française...',
      completed: 'Génération de sous-titres terminée. Voici le texte converti en français:'
    }
  };
  
  document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form submission
    
    document.getElementById('loading').style.display = 'block';
    
    document.getElementById('progress').style.display = 'block';
    
    document.getElementById('progress').innerHTML = '<div class="progress-bar" style="width: 0%"></div>';
    
    let progress = 0;
    const interval = setInterval(function() {
      progress += 10;
      document.querySelector('.progress-bar').style.width = progress + '%';
      if (progress >= 100) {
        clearInterval(interval);
        document.getElementById('loading').style.display = 'none';
        const language = document.getElementById('language').value;
        console.log(translations[language].processing);
        const convertedText = 'This is the converted text in ' + language + '.';
        document.getElementById('convertedText').innerText = translations[language].completed + '\n' + convertedText;
      }
    }, 300);
  });
  