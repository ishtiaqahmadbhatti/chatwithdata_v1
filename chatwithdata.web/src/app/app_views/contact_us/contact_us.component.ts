import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import Swal from 'sweetalert2';
import { HelpdeskService } from '../../app_services/helpdesk.service';

@Component({
    selector: 'app-contact-us',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule],
    templateUrl: './contact_us.component.html',
    styleUrl: './contact_us.component.css'
})
export class ContactUsComponent {
    contactForm: FormGroup;
    submitted = false;
    isProcessing = false;

    constructor(private fb: FormBuilder, private helpdeskService: HelpdeskService) {
        this.contactForm = this.fb.group({
            name: ['', Validators.required],
            email: ['', [Validators.required, Validators.email]],
            subject: ['', Validators.required],
            message: ['', Validators.required]
        });
    }

    onSubmit() {
        this.submitted = true;
        if (this.contactForm.valid) {
            this.isProcessing = true;
            this.helpdeskService.contactUs(this.contactForm.value).subscribe({
                next: (res) => {
                    this.isProcessing = false;
                    Swal.fire({
                        title: 'Message Sent!',
                        text: 'Thank you! Your message has been sent.',
                        icon: 'success',
                        confirmButtonColor: '#667eea'
                    });

                    this.contactForm.reset();
                    this.submitted = false;
                },
                error: (err) => {
                    this.isProcessing = false;
                    console.error('Error sending message:', err);
                    Swal.fire({
                        title: 'Error!',
                        text: 'Failed to send message. Please try again later.',
                        icon: 'error',
                        confirmButtonColor: '#e53e3e'
                    });
                }
            });
        }
    }
}
