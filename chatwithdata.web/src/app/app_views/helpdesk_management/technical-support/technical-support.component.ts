import { Component, ElementRef, HostListener, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import Swal from 'sweetalert2';
import { HelpdeskService } from '../../../app_services/helpdesk.service';

@Component({
    selector: 'app-technical-support',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule],
    templateUrl: './technical-support.component.html',
    styleUrl: './technical-support.component.css'
})
export class TechnicalSupportComponent {
    supportForm: FormGroup;
    submitted = false;
    isProcessing = false;
    selectedFile: File | null = null;
    selectedFileName: string = '';

    // Custom Dropdown Logic
    isIssueTypeDropdownOpen = false;
    issueTypes = [
        { label: 'Report a Bug', value: 'bug' },
        { label: 'Conversion Failure', value: 'conversion' },
        { label: 'Account Access', value: 'account' },
        { label: 'Billing Issue', value: 'billing' },
        { label: 'Other', value: 'other' }
    ];

    constructor(
        private fb: FormBuilder,
        private helpdeskService: HelpdeskService,
        private eRef: ElementRef
    ) {
        this.supportForm = this.fb.group({
            name: ['', Validators.required],
            email: ['', [Validators.required, Validators.email]],
            issueType: ['', Validators.required],
            description: ['', [Validators.required, Validators.minLength(20)]],
            attachment: [null]
        });
    }

    toggleIssueTypeDropdown() {
        this.isIssueTypeDropdownOpen = !this.isIssueTypeDropdownOpen;
    }

    selectIssueType(typeValue: string) {
        this.supportForm.patchValue({ issueType: typeValue });
        this.isIssueTypeDropdownOpen = false;
    }

    getSelectedIssueLabel(): string {
        const value = this.supportForm.get('issueType')?.value;
        const type = this.issueTypes.find(t => t.value === value);
        return type ? type.label : 'Select an issue...';
    }

    @ViewChild('issueTypeContainer') issueTypeContainer!: ElementRef;

    @HostListener('document:click', ['$event'])
    clickout(event: any) {
        if (this.issueTypeContainer && !this.issueTypeContainer.nativeElement.contains(event.target)) {
            this.isIssueTypeDropdownOpen = false;
        }
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
        if (this.supportForm.valid) {
            this.isProcessing = true;
            this.helpdeskService.submitTechnicalSupport(this.supportForm.value, this.selectedFile || undefined).subscribe({
                next: (res) => {
                    this.isProcessing = false;
                    Swal.fire({
                        title: 'Ticket Submitted!',
                        text: 'Support ticket created successfully! We will contact you soon.',
                        icon: 'success',
                        confirmButtonColor: '#667eea'
                    });

                    this.supportForm.reset();
                    this.selectedFile = null;
                    this.selectedFileName = '';
                    this.submitted = false;
                },
                error: (err) => {
                    this.isProcessing = false;
                    console.error('Error submitting ticket:', err);
                    Swal.fire({
                        title: 'Error!',
                        text: 'Failed to submit support ticket. Please try again later.',
                        icon: 'error',
                        confirmButtonColor: '#e53e3e'
                    });
                }
            });
        }
    }
}
