import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseMarkdownToolComponent } from '../base-markdown-tool.component';

@Component({
    selector: 'app-markdown-to-epub',
    imports: [CommonModule, FormsModule, FileConversionUiComponent],
    templateUrl: './markdown-to-epub.component.html',
    styleUrl: './markdown-to-epub.component.css',
    standalone: true
})
export class MarkdownToEpubComponent extends BaseMarkdownToolComponent {
    toolId = 'markdown-to-epub';
}
