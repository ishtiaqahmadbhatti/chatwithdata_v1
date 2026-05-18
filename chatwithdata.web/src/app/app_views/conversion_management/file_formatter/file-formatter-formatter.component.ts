import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { FILE_FORMATTER_TOOLS } from '../../../app_data/file-formatter-tools.data';
import { ConversionTool } from '../../../app_models/conversion-tool.model';
import { ConversionToolsUiComponent } from '../../../app_shared/conversion-tools-ui/conversion-tools-ui.component';

@Component({
    selector: 'app-file-formatter-main',
    standalone: true,
    imports: [CommonModule, ConversionToolsUiComponent],
    templateUrl: './file-formatter-formatter.component.html',
    styleUrl: './file-formatter-formatter.component.css'
})
export class FileFormatterComponent {
    tools: ConversionTool[] = FILE_FORMATTER_TOOLS;
}
