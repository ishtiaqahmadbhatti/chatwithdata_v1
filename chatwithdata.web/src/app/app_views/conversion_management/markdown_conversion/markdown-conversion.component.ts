import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MARKDOWN_CONVERSION_TOOLS } from '../../../app_data/markdown-conversion-tools.data';
import { ConversionTool } from '../../../app_models/conversion-tool.model';
import { ConversionToolsUiComponent } from '../../../app_shared/conversion-tools-ui/conversion-tools-ui.component';

@Component({
    selector: 'app-markdown-conversion',
    standalone: true,
    imports: [CommonModule, ConversionToolsUiComponent],
    templateUrl: './markdown-conversion.component.html',
    styleUrl: './markdown-conversion.component.css'
})
export class MarkdownConversionComponent {
    tools: ConversionTool[] = MARKDOWN_CONVERSION_TOOLS;
}
