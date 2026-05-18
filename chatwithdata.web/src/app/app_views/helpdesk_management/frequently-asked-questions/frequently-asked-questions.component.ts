import { Component, ElementRef, HostListener, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FAQ_DATA } from '../../../app_data/frequently-asked-questions.data';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HelpdeskService } from '../../../app_services/helpdesk.service';
import Swal from 'sweetalert2';

@Component({
    selector: 'app-frequently-asked-questions',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule],
    templateUrl: './frequently-asked-questions.component.html',
    styleUrl: './frequently-asked-questions.component.css'
})
export class FrequentlyAskedQuestionsComponent {
    @ViewChild('categoryDropdownContainer') categoryDropdownContainer!: ElementRef;
    faqData = FAQ_DATA;
    openCategoryIndex: number = 0;
    openQuestionIndex: number | null = null;

    faqForm: FormGroup;
    submitted = false;
    isProcessing = false;

    // Custom Dropdown Logic
    isCategoryDropdownOpen = false;

    constructor(
        private fb: FormBuilder,
        private helpdeskService: HelpdeskService,
        private eRef: ElementRef
    ) {
        this.faqForm = this.fb.group({
            name: ['', [Validators.required, Validators.minLength(2)]],
            question: ['', [Validators.required, Validators.minLength(10)]],
            category: ['', Validators.required],
            email: ['', [Validators.required, Validators.email]]
        });
    }

    toggleCategory(index: number) {
        if (this.openCategoryIndex !== index) {
            this.openCategoryIndex = index;
            this.openQuestionIndex = null;
        }
    }

    toggleQuestion(index: number) {
        if (this.openQuestionIndex === index) {
            this.openQuestionIndex = null;
        } else {
            this.openQuestionIndex = index;
        }
    }

    // Dropdown Handlers
    toggleCategoryDropdown() {
        this.isCategoryDropdownOpen = !this.isCategoryDropdownOpen;
    }

    selectCategoryDropdown(categoryName: string) {
        this.faqForm.patchValue({ category: categoryName });
        this.isCategoryDropdownOpen = false;
    }

    getSelectedCategoryLabel(): string {
        return this.faqForm.get('category')?.value || 'Select Category';
    }

    @HostListener('document:click', ['$event'])
    clickout(event: any) {
        if (this.categoryDropdownContainer && !this.categoryDropdownContainer.nativeElement.contains(event.target)) {
            this.isCategoryDropdownOpen = false;
        }
    }

    onSubmit() {
        this.submitted = true;
        if (this.faqForm.valid) {
            this.isProcessing = true;
            this.helpdeskService.submitFAQ(this.faqForm.value).subscribe({
                next: (res) => {
                    this.isProcessing = false;
                    Swal.fire({
                        title: 'Question Submitted!',
                        text: 'Thank you for your question. We will review it shortly.',
                        icon: 'success',
                        confirmButtonColor: '#ed8936'
                    });
                    this.faqForm.reset();
                    this.submitted = false;
                },
                error: (err) => {
                    this.isProcessing = false;
                    console.error('Error submitting FAQ:', err);
                    Swal.fire({
                        title: 'Error!',
                        text: 'Failed to submit question. Please try again later.',
                        icon: 'error',
                        confirmButtonColor: '#e53e3e'
                    });
                }
            });
        }
    }
}
