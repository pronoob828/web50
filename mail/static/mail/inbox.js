document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);


  // By default, load the inbox
  load_mailbox('inbox');

  // My code
  // Getting form submission
  document.querySelector("#compose-form").addEventListener("submit", (event) => {
    send_email();
    event.preventDefault();
  }); 

});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#open-email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}
 
function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#open-email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'block';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  get_emails(mailbox);
}

function send_email() {

  // Setting variables
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const content = document.querySelector('#compose-body').value;

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: content
    })
  })
    .then(response => response.json())
    .then(result => {
      console.log(result);
      load_mailbox('sent');
    })
    .catch(error => {
      console.log(error)
    });

}

function get_emails(mailbox) {

  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => load_emails(emails))
    .catch(error => {
      console.log(error)
    })
}

function load_emails(emails) {

  emails.forEach(email => {

    const email_container = document.createElement('div');

    // Sorry for shoving html here but I don't know a better way of doing this ...
    email_container.innerHTML = `
    <div class="col-8">
        <b>${email.sender}</b>
        <br>
        ${email.subject}
    </div>
    <div class='col-4'>
        ${email.timestamp}
    </div>
    `

    email_container.addEventListener('click', function () {
      open_email(email.id);
    });
    if (email.read) {
      email_container.style.backgroundColor = 'lightgray'
    }

    email_container.classList = "py-3 container-fluid d-flex border rounded my-1";
    document.querySelector('#emails-view').append(email_container);

  });
}

function open_email(id) {

  // Show email and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#open-email').style.display = 'block';

  main_div = document.querySelector('#open-email');
  main_div.classList = "container-fluid py-4";
  main_div.innerHTML = '';

  fetch(`emails/${id}`)
    .then(response => response.json())
    .then(email => {
      email_div = document.createElement('div');
      email_div.innerHTML = `
      <div class="d-flex">
          <div class='col-7'>
              <h3>From : ${email.sender}</h3>
              <h5>To : <small class="text-muted">${email.recipients}</small></h5>
              On : ${email.timestamp}
              <br>
              <b>Subject : ${email.subject} </b>
          </div>
          <div class='col-5 text-right'>
              <button id='reply-btn' class="btn-primary">
                  Reply
              </button>
              <button id='archive-btn' class="btn-secondary">
              Archive
              </button>
          </div>
      </div>
      <hr>
      <div class='container-fluid'>
          <p>${email.body} </p>
      </div>
      <hr>`

      main_div.append(email_div);
      set_read_true(id);

      reply_btn = document.querySelector('#reply-btn');
      reply_btn.addEventListener('click', function () {
        compose_email();
        document.querySelector('#compose-recipients').value = email.sender;
        document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
        document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body} `;
      })

      archive_btn = document.querySelector('#archive-btn');

      if (email.archived === true) {
        archive_btn.innerHTML = "Unarchive"
      } else {
        archive_btn.innerHTML = "Archive"
      }

      archive_btn.addEventListener('click', function () {
      
        function load_inbox(){
          load_mailbox('inbox');
        }

        if (email.archived === true) {
          fetch(`emails/${email.id}`, {
            method: 'PUT',
            body: JSON.stringify({
              archived: false
            })
          })
          document.querySelector('#archive-btn').innerHTML = 'Archive';
          const myTimeout = setTimeout(load_inbox, 50);

        }
        else {

          fetch(`emails/${email.id}`, {
            method: 'PUT',
            body: JSON.stringify({
              archived: true
            })
          })
          document.querySelector('#archive-btn').innerHTML = 'Unarchive';
          const myTimeout = setTimeout(load_inbox, 50);
        }

      })

    })
    .catch(error => console.log(error));
}

function set_read_true(id) {

  fetch(`emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  })

}
