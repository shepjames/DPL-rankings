// ============================================
// North Dallas Speech - Site JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', () => {

  // --- Mobile Navigation Toggle ---
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');

  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      const isOpen = navLinks.classList.contains('open');
      navToggle.setAttribute('aria-expanded', isOpen);
    });

    // Close mobile nav when a link is clicked
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // --- Navbar scroll effect ---
  const navbar = document.getElementById('navbar');
  if (navbar) {
    const onScroll = () => {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // --- FAQ Accordion ---
  document.querySelectorAll('.faq-question').forEach(button => {
    button.addEventListener('click', () => {
      const answer = button.nextElementSibling;
      const isOpen = button.getAttribute('aria-expanded') === 'true';

      // Close all other answers
      document.querySelectorAll('.faq-question').forEach(otherBtn => {
        if (otherBtn !== button) {
          otherBtn.setAttribute('aria-expanded', 'false');
          otherBtn.nextElementSibling.classList.remove('open');
        }
      });

      // Toggle current
      button.setAttribute('aria-expanded', !isOpen);
      answer.classList.toggle('open', !isOpen);
    });
  });

  // --- Contact Form (demo handler) ---
  const contactForm = document.getElementById('contactForm');
  const formSuccess = document.getElementById('formSuccess');

  if (contactForm && formSuccess) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
      // In production, this would send data to a backend or service like Formspree/Netlify Forms
      contactForm.style.display = 'none';
      formSuccess.style.display = 'block';
    });
  }

  // --- Smooth scroll-reveal animation ---
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -40px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Observe elements for scroll animation
  document.querySelectorAll(
    '.service-card, .service-detail-card, .feature, .testimonial-card, ' +
    '.team-member, .process-step, .faq-item, .contact-info-card, ' +
    '.affiliation-item, .investment-card'
  ).forEach(el => {
    el.classList.add('reveal');
    observer.observe(el);
  });
});

// --- Reveal animation CSS injection ---
const style = document.createElement('style');
style.textContent = `
  .reveal {
    opacity: 0;
    transform: translateY(24px);
    transition: opacity 0.6s ease, transform 0.6s ease;
  }
  .revealed {
    opacity: 1;
    transform: translateY(0);
  }
`;
document.head.appendChild(style);
