import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import Swal from 'sweetalert2';
import { HelpdeskService } from '../../../app_services/helpdesk.service';

@Component({
    selector: 'app-customer-feedback',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule],
    templateUrl: './customer-feedback.component.html',
    styleUrl: './customer-feedback.component.css'
})
export class CustomerFeedbackComponent {
    feedbackForm: FormGroup;
    submitted = false;
    isProcessing = false;
    ratings = [1, 2, 3, 4, 5];

    constructor(private fb: FormBuilder, private helpdeskService: HelpdeskService) {
        this.feedbackForm = this.fb.group({
            name: ['', Validators.required],
            email: ['', [Validators.required, Validators.email]],
            rating: [null, Validators.required],
            message: ['', [Validators.required, Validators.minLength(10)]]
        });
    }

    setRating(rating: number) {
        this.feedbackForm.patchValue({ rating });
    }

    onSubmit() {
        this.submitted = true;
        if (this.feedbackForm.valid) {
            this.isProcessing = true;

            // Map form values to expected API format (message -> feedback)
            const formData = {
                ...this.feedbackForm.value,
                feedback: this.feedbackForm.value.message
            };

            this.helpdeskService.shareFeedback(formData).subscribe({
                next: (res) => {
                    this.isProcessing = false;
                    Swal.fire({
                        title: 'Thank You!',
                        text: 'Your feedback has been submitted successfully!',
                        icon: 'success',
                        confirmButtonColor: '#9f7aea'
                    });
                    this.feedbackForm.reset();
                    this.submitted = false;
                },
                error: (err) => {
                    this.isProcessing = false;
                    console.error('Error submitting feedback:', err);
                    Swal.fire({
                        title: 'Error!',
                        text: 'Failed to submit feedback. Please try again later.',
                        icon: 'error',
                        confirmButtonColor: '#e53e3e'
                    });
                }
            });
        }
    }
}
