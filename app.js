// Define all functions first
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "<")
        .replace(/>/g, ">")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function renderEmails(emails) {
    const container = document.getElementById('emails-container');
    
    if (emails.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No emails found matching your criteria.</div>';
        return;
    }
    
    emails.forEach(email => {
        const emailCard = document.createElement('div');
        emailCard.className = 'card email-card mb-2';
        emailCard.innerHTML = `
            <div class="card-body" onclick="showEmail(${email.id})">
                <h5 class="card-title">${escapeHtml(email.subject)}</h5>
                <div class="card-subtitle mb-2 text-muted">
                    From: ${escapeHtml(email.from)} | Date: ${email.date}
                </div>
                <div class="email-snippet">
                    ${escapeHtml(email.body.substring(0, 100))}...
                </div>
            </div>
        `;
        container.appendChild(emailCard);
    });
}

function renderPagination(total, page, perPage) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    // Previous button
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${page === 1 ? 'disabled' : ''}`;
    prevLi.innerHTML = `<a class="page-link" href="#" onclick="changePage(${page - 1})">Previous</a>`;
    pagination.appendChild(prevLi);
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === page ? 'active' : ''}`;
        li.innerHTML = `<a class="page-link" href="#" onclick="changePage(${i})">${i}</a>`;
        pagination.appendChild(li);
    }
    
    // Next button
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${page === totalPages ? 'disabled' : ''}`;
    nextLi.innerHTML = `<a class="page-link" href="#" onclick="changePage(${page + 1})">Next</a>`;
    pagination.appendChild(nextLi);
}

function changePage(newPage) {
    if (newPage < 1 || newPage > totalPages) return;
    currentPage = newPage;
    loadEmails();
    window.scrollTo(0, 0);
}

function showEmail(id) {
    // fetch(`/emails?per_page=1&search=&sender=&from_date=&to_date=`)
    fetch(`/email?id=${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data)
            // const email = data.emails.find(e => e.id === id);
            
            // if (email) {
                const modal = new bootstrap.Modal(document.getElementById('emailModal'));
                document.getElementById('emailModalTitle').textContent = data.subject;
                document.getElementById('emailModalBody').textContent = data.body;
                modal.show();
            // }
            console.log("email test")
        })
        .catch(error => {
            console.error('Error fetching email:', error);
        });
}

// Main variables and initialization
let currentPage = 1;
const perPage = 20;
let totalPages = 1;

function loadEmails() {
    const search = document.getElementById('search').value;
    const sender = document.getElementById('sender').value;
    const fromDate = document.getElementById('from-date').value;
    const toDate = document.getElementById('to-date').value;
    
    document.getElementById('loading').style.display = 'block';
    document.getElementById('emails-container').innerHTML = '';
    
    const params = new URLSearchParams({
        page: currentPage,
        per_page: perPage,
        search: search,
        sender: sender,
        from_date: fromDate,
        to_date: toDate
    });
    
    fetch(`/emails?${params}`)
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Server error') });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            document.getElementById('loading').style.display = 'none';
            totalPages = data.total_pages;
            renderEmails(data.emails);
            renderPagination(data.total, data.page, data.per_page);
        })
        .catch(error => {
            console.error('Error fetching emails:', error);
            document.getElementById('loading').style.display = 'none';
            document.getElementById('emails-container').innerHTML = `
                <div class="alert alert-danger">
                    Error loading emails: ${error.message}
                </div>
            `;
        });
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    loadEmails();
    
    document.getElementById('apply-filters').addEventListener('click', () => {
        currentPage = 1;
        loadEmails();
    });
});
