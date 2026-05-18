import { Component, ElementRef, HostListener, ViewChild, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import Swal from 'sweetalert2';
import { HelpdeskService } from '../../../app_services/helpdesk.service';

// Import all tool data
import { PDF_CONVERSION_TOOLS } from '../../../app_data/pdf-conversion-tools.data';
import { IMAGE_CONVERSION_TOOLS } from '../../../app_data/image-conversion-tools.data';
import { AUDIO_CONVERSION_TOOLS } from '../../../app_data/audio-conversion-tools.data';
import { VIDEO_CONVERSION_TOOLS } from '../../../app_data/video-conversion-tools.data';
import { OFFICE_CONVERSION_TOOLS } from '../../../app_data/office-conversion-tools.data';
import { EBOOK_CONVERSION_TOOLS } from '../../../app_data/ebook-conversion-tools.data';
import { JSON_CONVERSION_TOOLS } from '../../../app_data/json-conversion-tools.data';
import { XML_CONVERSION_TOOLS } from '../../../app_data/xml-conversion-tools.data';
import { CSV_CONVERSION_TOOLS } from '../../../app_data/csv-conversion-tools.data';
import { TEXT_CONVERSION_TOOLS } from '../../../app_data/text-conversion-tools.data';
import { OCR_CONVERSION_TOOLS } from '../../../app_data/ocr-conversion-tools.data';
import { WEBSITE_CONVERSION_TOOLS } from '../../../app_data/website-conversion-tools.data';
import { SUBTITLE_CONVERSION_TOOLS } from '../../../app_data/subtitle-conversion-tools.data';
import { FILE_FORMATTER_TOOLS } from '../../../app_data/file-formatter-tools.data';
import { MARKDOWN_CONVERSION_TOOLS } from '../../../app_data/markdown-conversion-tools.data';

@Component({
    selector: 'app-tool-feedback',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule],
    templateUrl: './tool-feedback.component.html',
    styleUrl: './tool-feedback.component.css'
})
export class ToolFeedbackComponent implements OnInit {
    feedbackForm: FormGroup;
    submitted = false;
    isProcessing = false;
    ratings = [1, 2, 3, 4, 5];
    isLocked = false;

    // Tool Categories
    toolCategories: any[] = [
        { name: 'PDF Conversion', tools: PDF_CONVERSION_TOOLS.map(t => t.title) },
        { name: 'Image Conversion', tools: IMAGE_CONVERSION_TOOLS.map(t => t.title) },
        { name: 'Audio Conversion', tools: AUDIO_CONVERSION_TOOLS.map(t => t.title) },
        { name: 'Video Conversion', tools: VIDEO_CONVERSION_TOOLS.map(t => t.title) },
        { name: 'Office Conversion', tools: OFFICE_CONVERSION_TOOLS.map(t => t.title) },
        { name: 'E-Book Conversion', tools: EBOOK_CONVERSION_TOOLS.map(t => t.title) },
        { name: 'JSON Conversion', tools: JSON_CONVERSION_TOOLS.map(t => t.title) },
        { name: 'XML Conversion', tools: XML_CONVERSION_TOOLS.map(t => t.title) },
        { name: 'CSV Conversion', tools: CSV_CONVERSION_TOOLS.map(t => t.title) },
        { name: 'Text Conversion', tools: TEXT_CONVERSION_TOOLS.map(t => t.title) },
        { name: 'OCR Conversion', tools: OCR_CONVERSION_TOOLS.map(t => t.title) },
        { name: 'Website Conversion', tools: WEBSITE_CONVERSION_TOOLS.map(t => t.title) },
        { name: 'Subtitle Conversion', tools: SUBTITLE_CONVERSION_TOOLS.map(t => t.title) },
        { name: 'File Formatter', tools: FILE_FORMATTER_TOOLS.map(t => t.title) },
        { name: 'Markdown Conversion', tools: MARKDOWN_CONVERSION_TOOLS.map(t => t.title) }
    ];

    selectedTools: string[] = [];
    isCategoryDropdownOpen = false;
    isToolDropdownOpen = false;

    @ViewChild('categoryContainer') categoryContainer!: ElementRef;
    @ViewChild('toolContainer') toolContainer!: ElementRef;

    @HostListener('document:click', ['$event'])
    clickout(event: any) {
        // If clicking outside category dropdown, close it
        if (this.categoryContainer && !this.categoryContainer.nativeElement.contains(event.target)) {
            this.isCategoryDropdownOpen = false;
        }
        // If clicking outside tool dropdown, close it
        if (this.toolContainer && !this.toolContainer.nativeElement.contains(event.target)) {
            this.isToolDropdownOpen = false;
        }
    }

    constructor(
        private fb: FormBuilder,
        private eRef: ElementRef,
        private route: ActivatedRoute,
        private helpdeskService: HelpdeskService
    ) {
        this.feedbackForm = this.fb.group({
            name: ['', Validators.required],
            email: ['', [Validators.required, Validators.email]],
            category: ['', Validators.required],
            tool: ['', Validators.required],
            rating: [null, Validators.required],
            message: ['', [Validators.required, Validators.minLength(10)]]
        });
    }

    ngOnInit(): void {
        this.route.queryParams.subscribe(params => {
            const toolName = params['tool'];
            const categoryName = params['category'];
            if (toolName) {
                this.autoSelectTool(toolName, categoryName);
            } else {
                this.resetSelection();
            }
        });
    }

    autoSelectTool(toolName: string, categoryName?: string) {
        // Find category containing his tool, prioritizing explicit categoryName if provided
        let matchedCategory;

        if (categoryName) {
            matchedCategory = this.toolCategories.find(cat =>
                cat.name === categoryName && cat.tools.includes(toolName)
            );
        }

        if (!matchedCategory) {
            matchedCategory = this.toolCategories.find(cat => cat.tools.includes(toolName));
        }

        if (matchedCategory) {
            this.isLocked = true;
            this.selectedTools = matchedCategory.tools;

            this.feedbackForm.patchValue({
                category: matchedCategory.name,
                tool: toolName
            });
        }
    }

    resetSelection() {
        this.isLocked = false;
        this.selectedTools = [];
        this.isCategoryDropdownOpen = false;
        this.isToolDropdownOpen = false;

        this.feedbackForm.patchValue({
            category: '',
            tool: ''
        });
    }

    toggleCategoryDropdown() {
        if (this.isLocked) return;
        this.isCategoryDropdownOpen = !this.isCategoryDropdownOpen;
        this.isToolDropdownOpen = false;
    }

    toggleToolDropdown() {
        if (this.isLocked) return;
        if (this.selectedTools.length > 0) {
            this.isToolDropdownOpen = !this.isToolDropdownOpen;
            this.isCategoryDropdownOpen = false;
        }
    }

    selectCategory(categoryName: string) {
        if (this.isLocked) return;
        this.feedbackForm.patchValue({ category: categoryName });
        const category = this.toolCategories.find(c => c.name === categoryName);
        this.selectedTools = category ? category.tools : [];
        this.feedbackForm.patchValue({ tool: '' }); // Reset tool
        this.isCategoryDropdownOpen = false;
    }

    selectTool(toolName: string) {
        if (this.isLocked) return;
        this.feedbackForm.patchValue({ tool: toolName });
        this.isToolDropdownOpen = false;
    }

    setRating(rating: number) {
        this.feedbackForm.patchValue({ rating });
    }

    onSubmit() {
        this.submitted = true;
        if (this.feedbackForm.valid) {
            this.isProcessing = true;
            this.helpdeskService.submitToolFeedback(this.feedbackForm.value).subscribe({
                next: (res) => {
                    this.isProcessing = false;
                    Swal.fire({
                        title: 'Feedback Received!',
                        text: 'Thank you for helping us improve our tools!',
                        icon: 'success',
                        confirmButtonColor: '#667eea'
                    });

                    this.feedbackForm.reset();
                    this.selectedTools = [];
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
