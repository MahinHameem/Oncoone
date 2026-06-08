// static/assets/js/i18n.js
(function (global) {
  const STORAGE_KEY = 'site_lang';
  const DEFAULT = 'en';

  const translations = {
    en: {
      "nav.home": "Home",
      "nav.courses": "Courses",
      "nav.about": "About Us",
      "nav.contact": "Contact",
      "nav.payments": "Payments",
      "hero.title": "Canada's First Survivor-Led Oncology Esthetics Certificate",
      "hero.subtitle": "Empowering estheticians to care with skill, safety, and soul.",
      "hero.cta": "ENROLL NOW",
      "watch.founder.title": "Watch Our Founder on the Beauty Babble Podcast",
      "watch.founder.subtitle": "Inspire, educate, and transform your understanding with a survivor-led perspective.",
      "watch.now": "Watch Now on YouTube",
      "watch.founder.summary": "Founder Marilyn Sepe joined the Beauty Babble podcast to discuss oncology esthetics, compassionate client care, and advancing safe, trauma-informed support for individuals undergoing cancer treatment.",
      "speaking.book": "Book a Speaking Session",
      "speaking.subtitle": "Inspire, educate, and transform your audience with a survivor-led voice.",
      "speaking.description": "Marilyn is a cancer advocate, motivational speaker, and founder of OncoOne Aesthetic School. Her talks uplift, empower, and inspire audiences with hope and practical knowledge.",
      "video.fallback": "Your browser does not support the video tag.",
      "speaking.button": "Book Session",
      "speaking.modal.title": "Book Your Session",
      "modal.speaking.title": "Book Your Session",
      "page.title": "OncoOne | Aesthetic School",
      "form.full_name": "Full Name",
      "form.email": "Email Address",
      "form.phone": "Phone Number",
      "form.session_for": "Who is this session for?",
      "form.session_type": "Session Type",
      "form.mode": "Preferred Mode",
      "form.date": "Preferred Date",
      "form.time": "Preferred Time",
      "form.participants": "Number of Participants",
      "form.purpose": "Purpose of Booking",
      "form.notes": "Additional Notes",
      "form.book_button": "Book Session",
      "announcement.badge": "Workshop Announcement",
      "announcement.title": "Survivor-Led Cancer Nutrition Workshop",
      "announcement.list.1": "How cancer affects the body",
      "announcement.list.2": "Why nutrition matters during and after treatment",
      "announcement.list.3": "What truly helps from someone who has lived it",
      "announcement.list.4": "Practical, safe ways to support people with cancer",
      "announcement.date": "Date: Saturday, April 25",
      "announcement.time": "Time: 10:00 AM - 4:00 PM",
      "announcement.location": "Location: 700 Lawrence Ave West, Suite 370",
      "announcement.city": "Toronto, Ontario M6A 3B4 (in the Lawrence Allen Plaza)",
      "announcement.seats": "Seats: 20 only",
      "announcement.cost": "Cost: 349 CAD",
      "announcement.quote": "Cancer changes the body. Knowledge changes the journey.",
      "announcement.sold_out": "Sold Out",
      "announcement.register_now": "Register Now",
      "announcement.contact_us": "Contact Us",
      "speaking.loading": "Booking ...",
      "tools.course.description": "The <strong>Gold standard in Survivor-Sensitive Training</strong> — Ontario's first hands-on oncology esthetics course led by a cancer survivor.<br><br>Blending rigorous theory with compassionate, trauma-informed practice, it sets a benchmark for safe, empowering care. Students gain real-world protocols, survivor-sensitive techniques, and emotional insight — preparing them to serve with skill, dignity, and heart.",
      "tools.course.title": "The Resilience Course",
      "tools.waitlist": "Our 6 weeks course begins soon. Join the waiting list.",
      "tools.course.view": "View Course",
      "about.title": "About Us",
      "about.tab.founder": "Our Founder",
      "about.tab.mission": "Our Mission",
      "about.tab.vision": "Our Vision",
      "about.founder.paragraph": "Marilyn is a cancer survivor, nutritionist, and founder of Ontario's first advanced oncology esthetic certificate school. Her journey inspired a sanctuary of healing and empowerment for survivors and aestheticians alike. With decades of experience, she blends science, soul, and survivor wisdom into a trauma-informed, emotionally sensitive curriculum. Fluent in Italian and connected to her heritage, Marilyn champions diversity, mentorship, and international collaboration. <br><br>Through OncoOne, she empowers students to become ambassadors of healing, serving with empathy and purpose.",
      "about.founder.quote": "\"I didn't survive cancer to stay silent. I survived to teach. To heal. To leave something behind that matters. OncoOne™ is my legacy — a school where estheticians learn to care for survivors with skill, safety, and soul. This is my gift to Toronto, to Canada, and to every student who chooses to carry this mission forward.\"",
      "about.mission": "\"Empowering aestheticians with trauma-informed, survivor-sensitive training rooted in dignity, healing, and cultural respect.\"",
      "about.vision": "\"Through premium training, advocacy, and innovation, OncoOne will set the national standard for oncology aesthetics — cultivating a legacy of care that transforms lives, one touch at a time.\"",
      "tools.title": "Integrated Tools for Your Journey",
      "contact.title": "Contact Us",
      "contact.subtitle": "Get in touch with OncoOne Aesthetic School",
      "contact.card.phone.title": "Contact",
      "contact.card.address.title": "Address",
      "contact.card.address.lines": "700 Lawrence Ave West<br>(Lawrence Allen Plaza) Suite 370",
      "contact.card.schedule.title": "Schedule",
      "contact.card.schedule.label": "Office Hours:<br>",
      "contact.card.schedule.hours": "10 AM - 5:30 PM",
      "contact.medix.text": "Our School operates from Medix College North York Campus",
      "partners.title": "Our Partners",
      "partners.subtitle": "We proudly collaborate with innovative organizations who share our vision of excellence.",
      "workshop.register_label": "Register for Cancer Nutrition Workshop",
      "workshop.form.full_name": "Full Name",
      "workshop.form.email": "Email Address",
      "workshop.form.contact": "Contact Number",
      "workshop.form.referral": "How did you hear about us?",
      "workshop.form.select_option": "Select an option",
      "workshop.form.option.social": "Social Media (Facebook, Instagram)",
      "workshop.form.option.friend": "Friend / Family Recommendation",
      "workshop.form.option.website": "Website / Blog",
      "workshop.form.option.webinar": "Webinar / Workshop",
      "workshop.form.option.school": "School / University",
      "workshop.form.option.other": "Other (Please specify)",
      "workshop.submit": "Submit Registration",
      "products.learn.7": "Featuring guest speakers: nurses, oncologists & survivor advocates",
      "products.learn.note": "<strong>Featuring guest speakers</strong> including oncology nurses, oncologists, and survivor advocates.",
      "products.instructor.subtitle": "Marilyn — certified medical esthetics instructor, cancer survivor & advocate with 20+ years experience.",
      "products.instructor.title": "👩‍⚕️ About the Instructor",
      "products.instructor.1": "Certified Nutritionist & Medical Esthetics Expert",
      "products.instructor.2": "20+ years in skincare & oncology esthetics",
      "products.instructor.5": "Author of Nonna Ma's Cancer Survivor Cookbook",
      "products.audience.title": "🎓 Who Should Join?",
      "products.audience.subtitle": "Designed for professionals passionate about compassionate oncology esthetic care.",
      "products.audience.1": "Medical estheticians & spa professionals",
      "products.audience.2": "Nurses & skincare therapists",
      "products.audience.3": "Students & transitioning professionals",
      "products.audience.4": "Anyone passionate about holistic wellness",
      "products.delivery.title": "📍 Format & Delivery",
      "products.delivery.subtitle": "Hands-on, in-person training plus expert talks.",
      "products.delivery.duration": "Duration: 40 hours (certification)",
      "products.delivery.practice": "Hands-on, in-person practice",
      "products.delivery.speakers": "Guest speakers & real-world case studies",
      "products.delivery.certificate": "Certificate awarded upon successful completion",
      "products.delivery.schedule": "<strong>Tuesday and Thursday 5-9 for 6 weeks OR Saturday 9-5 for 6 weeks.</strong>",
      "products.prerequisite.title": "Prerequisite Requirement",
      "products.prerequisite.heading": "Before you enroll",
      "products.prerequisite.description": "To join the full Oncology Esthetics Certificate, please either hold an esthetics-related credential or complete our Bridge course first.",
      "products.prerequisite.item.1": "A certificate or diploma in esthetics or a related field.",
      "products.prerequisite.item.2": "A letter from an employer verifying hands-on esthetics experience.",
      "products.prerequisite.item.3": "Completion of our <strong>Pre-Certificate Bridge Course</strong> for those without formal training.",
      "products.prerequisite.note": "<strong>Upload Proof of Prerequisite</strong> is required during registration. Accepted formats: <strong>PDF, JPG, PNG</strong>. Max file size: <strong>5MB</strong>.",
      "products.prerequisite.button.register": "Proceed to Registration",
      "products.prerequisite.button.bridge": "View Bridge Course",
      "products.bridge.includes.title": "Course Includes:",
      "products.bridge.includes.1": "Skin Anatomy & Facial Mapping",
      "products.bridge.includes.2": "Product Safety & Technique Awareness",
      "products.bridge.includes.3": "Infection Control & Professional Image",
      "products.bridge.includes.4": "Common Skin Conditions & Treatment Awareness",
      "products.bridge.includes.5": "Final Quiz & Certification",
      "products.bridge.title": "Pre-Certificate Bridge Course",
      "products.bridge.overview.title": "Bridge Course Overview",
      "products.bridge.overview.description": "A practical pathway for aspiring estheticians without formal qualifications to prepare safely for oncology-focused care.",
      "products.bridge.detail.duration": "<strong>Duration:</strong> 20 hours",
      "products.bridge.detail.format": "<strong>Format:</strong> In-person training",
      "products.bridge.detail.schedule": "<strong>Scheduling Options:</strong> 3 Saturdays or 5 evenings (final schedule based on availability)",
      "products.bridge.detail.price": "<strong>Price:</strong> $745.00 + Roots & Release Kit",
      "products.bridge.detail.certification": "<strong>Certification:</strong> Certificate of Completion included",
      "products.bridge.button.register": "Register for Bridge Course",
      "products.registration.title": "Register for the Course",
      "products.registration.heading": "Registration",
      "products.registration.description": "Please tell us whether you meet the prerequisite qualification below.",
      "products.registration.course_question": "Which course would you like to register for? <span class=\"required-star\">*</span>",
      "products.registration.course.bridge.title": "Pre-Certificate Bridge Course",
      "products.registration.course.bridge.subtitle": "(For those without esthetics certification)",
      "products.registration.course.oncology.title": "Oncology Esthetics Certificate",
      "products.registration.course.oncology.subtitle": "(Full Program - Requires prerequisite)",
      "products.registration.course.workshop.title": "Cancer Nutrition Workshop",
      "products.registration.course.workshop.subtitle": "(One-day seminar - 20 seats only)",
      "products.registration.course.workshop.sold_out": " - SOLD OUT",
      "products.registration.qualification_question": "Do you have the above-mentioned qualifications? <span class=\"required-star\">*</span>",
      "products.registration.qualification.yes": "Yes — I have a certificate / employer verification",
      "products.registration.qualification.no": "No — I do not have prerequisites (will suggest Bridge Course)",
      "products.registration.proof_label": "Upload Proof of Prerequisite <span class=\"required-star\">*</span>",
      "products.registration.proof_help": "Accepted formats: PDF, JPG, PNG — Max size: 5MB.",
      "products.registration.referral_label": "How did you hear about us? <span class=\"required-star\">*</span>",
      "products.registration.referral.select_option": "Select an option",
      "products.registration.referral.option.social": "Social Media (Facebook, Instagram)",
      "products.registration.referral.option.friend": "Friend / Family Recommendation",
      "products.registration.referral.option.website": "Website / Blog",
      "products.registration.referral.option.webinar": "Webinar / Workshop",
      "products.registration.referral.option.school": "School / University",
      "products.registration.referral.option.other": "Other (Please specify)",
      "products.registration.referral.other_placeholder": "Please specify",
      "products.registration.contact_label": "Contact Number <span class=\"required-star\">*</span>",
      "products.registration.submit": "Submit Registration",
      "products.registration.bridge_note": "💡 You don't have a certificate. You can take our <strong>Pre-Certificate Bridge Course</strong> first, or register for both!",
      "products.book.note": "🎁 <strong>Nonna Ma's Cancer Survivor Cookbook</strong> is complimentary upon course registration.",
      "products.book.title": "Nonna Ma's Cancer Survivor Cookbook",
      "products.book.subtitle": "\"The Art of Modern Aesthetics\"",
      "products.book.description": "Dive into the science and artistry of oncology-focused esthetics with this practical cookbook and guide. Complimentary for all students who register for any full or bridge course.",
      "section.tools.title": "Integrated Tools for Your Journey",
      "products.title": "Oncology Esthetics Certification",
      "products.full_certificate": "Full Oncology Esthetics Certificate",
      "products.duration_price": "Duration: 40 hours | Price: $1,999.00",
      "products.duration_price": "Duration: 40 hours | Price: $1,999.00",
      "btn.register": "Register",
      "products.what_you_will_learn": "What You Will Learn",
      "products.hero.summary": "A 40-hour professional certification designed to train estheticians and allied professionals in safe, trauma-informed, oncology-focused skincare and client care.",
      "products.learn.1": "Understanding cancer and treatment impacts across the body",
      "products.learn.2": "Post-surgical skin and emotional recovery",
      "products.learn.3": "Adapting esthetic protocols for oncology-safe practice",
      "products.learn.4": "Lymphedema awareness & gentle lymphatic techniques",
      "products.learn.5": "Ingredient safety, fragile skin protocols, oncology nail care",
      "products.learn.6": "Emotional literacy & mental wellness in esthetic care",
      "section.tools.title": "Integrated Tools for Your Journey",
      "footer.copy": "© 2025 OncoOne. All rights reserved.",
      "footer.powered_by": "Powered by Matrix Labs",
      "empowering.tagline": "Empowering Post-Cancer Thriving"
    },
    es: {
      "nav.home": "Inicio",
      "nav.courses": "Cursos",
      "nav.about": "Sobre Nosotros",
      "nav.contact": "Contacto",
      "nav.payments": "Pagos",
      "hero.title": "El primer certificado de estética oncológica dirigido por sobrevivientes en Canadá",
      "hero.subtitle": "Empoderando a las esteticistas para cuidar con habilidad, seguridad y alma.",
      "hero.cta": "INSCRÍBETE AHORA",
      "watch.founder.title": "Mira a nuestra fundadora en el podcast Beauty Babble",
      "watch.founder.subtitle": "Inspira, educa y transforma tu comprensión con una perspectiva liderada por sobrevivientes.",
      "watch.now": "Ver ahora en YouTube",
      "watch.founder.summary": "La fundadora Marilyn Sepe se unió al podcast Beauty Babble para hablar sobre estética oncológica, atención al cliente compasiva y avanzar en el apoyo seguro e informado por el trauma para personas que atraviesan tratamiento contra el cáncer.",
      "speaking.book": "Reserva una sesión de ponencia",
      "speaking.subtitle": "Inspira, educa y transforma a tu audiencia con una voz liderada por sobrevivientes.",
      "speaking.description": "Marilyn es una defensora del cáncer, conferencista motivacional y fundadora de OncoOne Aesthetic School. Sus charlas elevan, empoderan e inspiran a las audiencias con esperanza y conocimientos prácticos.",
      "video.fallback": "Tu navegador no es compatible con la etiqueta de video.",
      "speaking.button": "Reservar sesión",
      "modal.speaking.title": "Reserva tu sesión",
      "page.title": "OncoOne | Escuela de Estética",
      "form.full_name": "Nombre completo",
      "form.email": "Dirección de correo",
      "form.phone": "Número de teléfono",
      "form.session_for": "¿Para quién es esta sesión?",
      "form.session_type": "Tipo de sesión",
      "form.mode": "Modo preferido",
      "form.date": "Fecha preferida",
      "form.time": "Hora preferida",
      "form.participants": "Número de participantes",
      "form.purpose": "Propósito de la reserva",
      "form.notes": "Notas adicionales",
      "form.book_button": "Reservar sesión",
      "announcement.badge": "Anuncio de taller",
      "announcement.title": "Taller de nutrición para el cáncer dirigido por sobrevivientes",
      "announcement.list.1": "Cómo el cáncer afecta el cuerpo",
      "announcement.list.2": "Por qué la nutrición importa durante y después del tratamiento",
      "announcement.list.3": "Lo que realmente ayuda desde alguien que lo ha vivido",
      "announcement.list.4": "Maneras prácticas y seguras de apoyar a las personas con cáncer",
      "announcement.date": "Fecha: Sábado, 25 de abril",
      "announcement.time": "Hora: 10:00 - 16:00",
      "announcement.location": "Ubicación: 700 Lawrence Ave West, Suite 370",
      "announcement.city": "Toronto, Ontario M6A 3B4 (en Lawrence Allen Plaza)",
      "announcement.seats": "Plazas: solo 20",
      "announcement.cost": "Costo: 349 CAD",
      "announcement.quote": "El cáncer cambia el cuerpo. El conocimiento cambia el camino.",
      "announcement.sold_out": "Agotado",
      "announcement.register_now": "Registrarse ahora",
      "announcement.contact_us": "Contáctanos",
      "speaking.loading": "Reservando ...",
      "tools.course.description": "El <strong>estándar de oro en capacitación sensible a sobrevivientes</strong> — el primer curso práctico de estética oncológica en Ontario dirigido por una sobreviviente de cáncer.<br><br>Combinando teoría rigurosa con práctica compasiva e informada por el trauma, establece un referente para una atención segura y empoderadora. Los estudiantes obtienen protocolos del mundo real, técnicas sensibles a sobrevivientes e información emocional, preparándolos para servir con habilidad, dignidad y corazón.",
      "tools.course.title": "El curso de resiliencia",
      "tools.waitlist": "Nuestro curso de 6 semanas comienza pronto. Únete a la lista de espera.",
      "tools.course.view": "Ver curso",
      "about.title": "Sobre Nosotros",
      "about.tab.founder": "Nuestra Fundadora",
      "about.tab.mission": "Nuestra Misión",
      "about.tab.vision": "Nuestra Visión",
      "about.founder.paragraph": "Marilyn es sobreviviente de cáncer, nutricionista y fundadora de la primera escuela de certificación avanzada en estética oncológica de Ontario. Su viaje inspiró un santuario de sanación y empoderamiento para sobrevivientes y esteticistas por igual. Con décadas de experiencia, combina ciencia, alma y sabiduría de sobrevivientes en un plan de estudios sensible al trauma y emocionalmente cuidadoso. Fluida en italiano y conectada con su herencia, Marilyn defiende la diversidad, la mentoría y la colaboración internacional. <br><br>A través de OncoOne, empodera a los estudiantes para convertirse en embajadores de la sanación, sirviendo con empatía y propósito.",
      "about.founder.quote": "\"No sobreviví al cáncer para quedarme en silencio. Sobreviví para enseñar. Para sanar. Para dejar algo atrás que importe. OncoOne™ es mi legado — una escuela donde las esteticistas aprenden a cuidar a los sobrevivientes con habilidad, seguridad y alma. Este es mi regalo para Toronto, para Canadá y para cada estudiante que decide llevar adelante esta misión.\"",
      "about.mission": "\"Empoderar a las esteticistas con capacitación informada por el trauma, sensible a sobrevivientes, arraigada en la dignidad, la sanación y el respeto cultural.\"",
      "about.vision": "\"A través de capacitación premium, defensa e innovación, OncoOne establecerá el estándar nacional para la estética oncológica — cultivando un legado de cuidado que transforma vidas, un toque a la vez.\"",
      "tools.title": "Herramientas integradas para tu viaje",
      "contact.title": "Contáctanos",
      "contact.subtitle": "Ponte en contacto con OncoOne Aesthetic School",
      "contact.card.phone.title": "Contacto",
      "contact.card.address.title": "Dirección",
      "contact.card.address.lines": "700 Lawrence Ave West<br>(Lawrence Allen Plaza) Suite 370",
      "contact.card.schedule.title": "Horario",
      "contact.card.schedule.label": "Horario de oficina:<br>",
      "contact.card.schedule.hours": "10 AM - 5:30 PM",
      "contact.medix.text": "Nuestra escuela opera desde el campus de Medix College North York",
      "partners.title": "Nuestros Socios",
      "partners.subtitle": "Colaboramos con orgullo con organizaciones innovadoras que comparten nuestra visión de excelencia.",
      "workshop.register_label": "Registrarse para el Taller de Nutrición contra el Cáncer",
      "workshop.form.full_name": "Nombre completo",
      "workshop.form.email": "Dirección de correo",
      "workshop.form.contact": "Número de contacto",
      "workshop.form.referral": "¿Cómo te enteraste de nosotros?",
      "workshop.form.select_option": "Selecciona una opción",
      "workshop.form.option.social": "Redes sociales (Facebook, Instagram)",
      "workshop.form.option.friend": "Recomendación de un amigo / familiar",
      "workshop.form.option.website": "Sitio web / Blog",
      "workshop.form.option.webinar": "Webinar / Taller",
      "workshop.form.option.school": "Escuela / Universidad",
      "workshop.form.option.other": "Otro (por favor especifica)",
      "workshop.submit": "Enviar registro",
      "products.learn.7": "Ponentes invitados: enfermeras, oncólogos y defensores sobrevivientes",
      "products.learn.note": "<strong>Ponentes invitados</strong> incluyendo enfermeras oncológicas, oncólogos y defensores sobrevivientes.",
      "products.instructor.subtitle": "Marilyn — instructora certificada en estética médica, sobreviviente de cáncer y defensora con más de 20 años de experiencia.",
      "products.instructor.title": "👩‍⚕️ Sobre la instructora",
      "products.instructor.1": "Nutricionista certificada y experta en estética médica",
      "products.instructor.2": "Más de 20 años en cuidado de la piel y estética oncológica",
      "products.instructor.5": "Autora del libro de cocina para sobrevivientes de cáncer de Nonna Ma",
      "products.audience.title": "🎓 ¿Quién debería unirse?",
      "products.audience.subtitle": "Diseñado para profesionales apasionados por el cuidado estético oncológico con compasión.",
      "products.audience.1": "Esteticistas médicos y profesionales de spa",
      "products.audience.2": "Enfermeras y terapeutas de cuidado de la piel",
      "products.audience.3": "Estudiantes y profesionales en transición",
      "products.audience.4": "Cualquiera apasionado por el bienestar holístico",
      "products.delivery.title": "📍 Formato y entrega",
      "products.delivery.subtitle": "Entrenamiento práctico presencial más charlas de expertos.",
      "products.delivery.duration": "Duración: 40 horas (certificación)",
      "products.delivery.practice": "Práctica práctica presencial",
      "products.delivery.speakers": "Ponentes invitados y estudios de casos del mundo real",
      "products.delivery.certificate": "Certificado otorgado tras la finalización exitosa",
      "products.delivery.schedule": "<strong>Martes y jueves 5-9 durante 6 semanas O sábado 9-5 durante 6 semanas.</strong>",
      "products.prerequisite.title": "Requisito previo",
      "products.prerequisite.heading": "Antes de inscribirte",
      "products.prerequisite.description": "Para unirte al Certificado de Estética Oncológica completo, por favor ten una credencial relacionada con estética o completa primero nuestro curso puente.",
      "products.prerequisite.item.1": "Un certificado o diploma en estética o un campo relacionado.",
      "products.prerequisite.item.2": "Una carta de un empleador que verifique experiencia práctica en estética.",
      "products.prerequisite.item.3": "Finalización de nuestro <strong>Curso puente de pre-certificación</strong> para quienes no tienen formación formal.",
      "products.prerequisite.note": "<strong>Se requiere cargar comprobante de requisito</strong> durante el registro. Formatos aceptados: <strong>PDF, JPG, PNG</strong>. Tamaño máximo de archivo: <strong>5MB</strong>.",
      "products.prerequisite.button.register": "Continuar al registro",
      "products.prerequisite.button.bridge": "Ver curso puente",
      "products.bridge.includes.title": "El curso incluye:",
      "products.bridge.includes.1": "Anatomía de la piel y mapeo facial",
      "products.bridge.includes.2": "Seguridad de productos y conciencia de técnicas",
      "products.bridge.includes.3": "Control de infecciones e imagen profesional",
      "products.bridge.includes.4": "Condiciones comunes de la piel y conciencia de tratamiento",
      "products.bridge.includes.5": "Examen final y certificación",
      "products.bridge.title": "Curso puente de pre-certificación",
      "products.bridge.overview.title": "Resumen del curso puente",
      "products.bridge.overview.description": "Un camino práctico para aspirantes a esteticistas sin calificaciones formales para prepararse de forma segura en el cuidado centrado en oncología.",
      "products.bridge.detail.duration": "<strong>Duración:</strong> 20 horas",
      "products.bridge.detail.format": "<strong>Formato:</strong> Capacitación presencial",
      "products.bridge.detail.schedule": "<strong>Opciones de programación:</strong> 3 sábados o 5 tardes (horario final según disponibilidad)",
      "products.bridge.detail.price": "<strong>Precio:</strong> $745.00 + Roots & Release Kit",
      "products.bridge.detail.certification": "<strong>Certificación:</strong> Certificado de finalización incluido",
      "products.bridge.button.register": "Registrarse en el curso puente",
      "products.registration.title": "Registrarse en el curso",
      "products.registration.heading": "Registro",
      "products.registration.description": "Por favor dinos si cumples con la calificación previa a continuación.",
      "products.registration.course_question": "¿Para qué curso te gustaría registrarte? <span class=\"required-star\">*</span>",
      "products.registration.course.bridge.title": "Curso puente de pre-certificación",
      "products.registration.course.bridge.subtitle": "(Para quienes no tienen certificación en estética)",
      "products.registration.course.oncology.title": "Certificado de estética oncológica",
      "products.registration.course.oncology.subtitle": "(Programa completo - requiere requisito)",
      "products.registration.course.workshop.title": "Taller de nutrición contra el cáncer",
      "products.registration.course.workshop.subtitle": "(Seminario de un día - solo 20 plazas)",
      "products.registration.course.workshop.sold_out": " - AGOTADO",
      "products.registration.qualification_question": "¿Tienes las calificaciones mencionadas anteriormente? <span class=\"required-star\">*</span>",
      "products.registration.qualification.yes": "Sí — Tengo un certificado / verificación del empleador",
      "products.registration.qualification.no": "No — No tengo prerrequisitos (se sugerirá el curso puente)",
      "products.registration.proof_label": "Subir comprobante de requisito <span class=\"required-star\">*</span>",
      "products.registration.proof_help": "Formatos aceptados: PDF, JPG, PNG — Tamaño máximo: 5MB.",
      "products.registration.referral_label": "¿Cómo te enteraste de nosotros? <span class=\"required-star\">*</span>",
      "products.registration.referral.select_option": "Selecciona una opción",
      "products.registration.referral.option.social": "Redes sociales (Facebook, Instagram)",
      "products.registration.referral.option.friend": "Recomendación de un amigo / familiar",
      "products.registration.referral.option.website": "Sitio web / Blog",
      "products.registration.referral.option.webinar": "Webinar / Taller",
      "products.registration.referral.option.school": "Escuela / Universidad",
      "products.registration.referral.option.other": "Otro (por favor especifica)",
      "products.registration.referral.other_placeholder": "Por favor especifica",
      "products.registration.contact_label": "Número de contacto <span class=\"required-star\">*</span>",
      "products.registration.submit": "Enviar registro",
      "products.registration.bridge_note": "💡 No tienes un certificado. Puedes tomar nuestro <strong>Curso puente de pre-certificación</strong> primero, o registrarte en ambos.",
      "products.book.note": "🎁 <strong>El libro de cocina para sobrevivientes de cáncer de Nonna Ma</strong> es complementario al registrarte en el curso.",
      "products.book.title": "El libro de cocina para sobrevivientes de cáncer de Nonna Ma",
      "products.book.subtitle": "\"El arte de la estética moderna\"",
      "products.book.description": "Sumérgete en la ciencia y el arte de la estética enfocada en oncología con este práctico libro de cocina y guía. Complementario para todos los estudiantes que se registren en cualquier curso completo o puente.",
      "section.tools.title": "Herramientas integradas para tu viaje",
      "products.title": "Certificación en Estética Oncológica",
      "products.full_certificate": "Certificado Completo de Estética Oncológica",
      "products.duration_price": "Duración: 40 horas | Precio: $1,999.00",
      "btn.register": "Registrarse",
      "products.what_you_will_learn": "Qué aprenderás",
      "products.hero.summary": "Una certificación profesional de 40 horas diseñada para capacitar a esteticistas y profesionales aliados en cuidado de la piel y atención oncológica segura, informada por el trauma.",
      "products.learn.1": "Comprender cómo el cáncer y los tratamientos afectan el cuerpo",
      "products.learn.2": "Piel postquirúrgica y recuperación emocional",
      "products.learn.3": "Adaptar protocolos estéticos para prácticas seguras en oncología",
      "products.learn.4": "Conciencia de linfedema y técnicas linfáticas suaves",
      "products.learn.5": "Seguridad de ingredientes, protocolos para piel frágil, cuidado oncológico de uñas",
      "products.learn.6": "Alfabetización emocional y bienestar mental en el cuidado estético",
      "section.tools.title": "Herramientas integradas para tu viaje",
      "footer.copy": "© 2025 OncoOne. Todos los derechos reservados.",
      "footer.powered_by": "Desarrollado por Matrix Labs",
      "empowering.tagline": "Empoderando la prosperidad post-cáncer"
    }
  };

  function getSavedLang() {
    try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
  }
  function saveLang(lang) {
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) { /* ignore */ }
  }
  function resolveLang(lang) {
    if (!lang) lang = getSavedLang() || DEFAULT;
    if (!translations[lang]) lang = DEFAULT;
    return lang;
  }
  function t(key, lang) {
    lang = resolveLang(lang);
    const ns = translations[lang] || {};
    return (ns[key] !== undefined) ? ns[key] : (translations[DEFAULT][key] || key);
  }

  function parseAttrMap(str) {
    if (!str) return [];
    return str.split(';').map(pair => {
      const idx = pair.indexOf(':');
      if (idx === -1) return null;
      const attr = pair.slice(0, idx).trim();
      const key = pair.slice(idx + 1).trim();
      return attr && key ? { attr, key } : null;
    }).filter(Boolean);
  }

  function translateElement(el, lang) {
    const key = el.getAttribute('data-i18n');
    if (key !== null) {
      const text = t(key, lang);
      el.textContent = text;
    }
    const htmlKey = el.getAttribute('data-i18n-html');
    if (htmlKey !== null) {
      el.innerHTML = t(htmlKey, lang);
    }
    const attrMap = el.getAttribute('data-i18n-attr');
    if (attrMap) {
      const list = parseAttrMap(attrMap);
      list.forEach(({ attr, key }) => {
        const value = t(key, lang);
        if (attr === 'value') el.value = value;
        else el.setAttribute(attr, value);
      });
    }
  }

  function translatePage(lang) {
    lang = resolveLang(lang);
    const els = document.querySelectorAll('[data-i18n], [data-i18n-html], [data-i18n-attr]');
    els.forEach(el => translateElement(el, lang));
    document.documentElement.lang = lang;
  }

  function setActiveSwitcherUI(lang, root = document) {
    const buttons = root.querySelectorAll('[data-lang-button]');
    buttons.forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-lang-button') === lang);
      btn.setAttribute('aria-pressed', btn.classList.contains('active') ? 'true' : 'false');
    });
    const selects = root.querySelectorAll('select[data-lang-select]');
    selects.forEach(sel => { sel.value = lang; });
  }

  function setupSwitcher(root = document) {
    root.addEventListener('click', (ev) => {
      const btn = ev.target.closest('[data-lang-button]');
      if (!btn) return;
      const lang = btn.getAttribute('data-lang-button');
      if (!lang) return;
      I18n.setLanguage(lang);
    });
    root.addEventListener('change', (ev) => {
      const sel = ev.target.closest('select[data-lang-select]');
      if (!sel) return;
      const lang = sel.value;
      I18n.setLanguage(lang);
    });
  }

  const I18n = {
    init(options = {}) {
      const defaultLang = options.defaultLang || DEFAULT;
      if (options.translations && typeof options.translations === 'object') {
        Object.keys(options.translations).forEach(k => {
          translations[k] = Object.assign({}, translations[k] || {}, options.translations[k]);
        });
      }
      const lang = resolveLang() || defaultLang;
      translatePage(lang);
      setActiveSwitcherUI(lang);
      setupSwitcher(document);
      if (typeof options.onInit === 'function') options.onInit(lang);
    },

    translatePage(lang) { translatePage(lang); setActiveSwitcherUI(lang); },
    setLanguage(lang) { if (!translations[lang]) return; saveLang(lang); translatePage(lang); setActiveSwitcherUI(lang); },
    getLanguage() { return resolveLang(); },
    t,
    translations
  };

  global.I18n = I18n;
})(window);
