import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { CSV_CONVERSION_TOOLS } from '../../../app_data/csv-conversion-tools.data';
import { ConversionTool } from '../../../app_models/conversion-tool.model';
import { ConversionToolsUiComponent } from '../../../app_shared/conversion-tools-ui/conversion-tools-ui.component';

@Component({
    selector: 'app-csv-conversion',
    standalone: true,
    imports: [CommonModule, ConversionToolsUiComponent],
    templateUrl: './csv-conversion.component.html',
    styleUrl: './csv-conversion.component.css'
})
export class CsvConversionComponent {
    tools: ConversionTool[] = CSV_CONVERSION_TOOLS;
}
