import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import Swal from 'sweetalert2';
import { HelpdeskService } from '../../../app_services/helpdesk.service';

@Component({
    selector: 'app-customer-queries',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule],
    templateUrl: './customer-queries.component.html',
    styleUrl: './customer-queries.component.css'
})
export class CustomerQueriesComponent {
    queryForm: FormGroup;
    submitted = false;
    isProcessing = false;
    selectedFile: File | null = null;
    selectedFileName: string = '';

    constructor(private fb: FormBuilder, private helpdeskService: HelpdeskService) {
        this.queryForm = this.fb.group({
            name: ['', Validators.required],
            email: ['', [Validators.required, Validators.email]],
            subject: ['', [Validators.required, Validators.minLength(5)]],
            query: ['', [Validators.required, Validators.minLength(20)]],
            attachment: [null]
        });
    }

    onFileChange(event: any) {
        const file = event.target.files[0];
        if (file) {
            this.selectedFile = file;
            this.selectedFileName = file.name;
        }
    }

    onSubmit() {
        this.submitted = true;
        if (this.queryForm.valid) {
            this.isProcessing = true;
            this.helpdeskService.submitQuery(this.queryForm.value, this.selectedFile || undefined).subscribe({
                next: (res) => {
                    this.isProcessing = false;
                    Swal.fire({
                        title: 'Query Submitted!',
                        text: 'Your query has been submitted! We will get back to you shortly.',
                        icon: 'success',
                        confirmButtonColor: '#ed8936'
                    });

                    this.queryForm.reset();
                    this.selectedFile = null;
                    this.selectedFileName = '';
                    this.submitted = false;
                },
                error: (err) => {
                    this.isProcessing = false;
                    console.error('Error submitting query:', err);
                    Swal.fire({
                        title: 'Error!',
                        text: 'Failed to submit query. Please try again later.',
                        icon: 'error',
                        confirmButtonColor: '#e53e3e'
                    });
                }
            });
        }
    }
}
