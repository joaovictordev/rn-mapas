$(document)
    .ready(function() {
      $('.ui.form')
        .form({
          fields: {
            email: {
              identifier  : 'email',
              rules: [
                {
                  type   : 'empty',
                  prompt : 'Por favor, entre com o seu email'
                },
                {
                  type   : 'email',
                  prompt : 'Por favor, entre com um email válido'
                }
              ]
            },
            password: {
              identifier  : 'password',
              rules: [
                {
                  type   : 'empty',
                  prompt : 'Por favor, entre com a sua senha'
                },
                {
                  type   : 'length[6]',
                  prompt : 'Sua senha deve ter no mínimo 6 caracteres'
                }
              ]
            }
          }
        })
      ;
    })
  ;