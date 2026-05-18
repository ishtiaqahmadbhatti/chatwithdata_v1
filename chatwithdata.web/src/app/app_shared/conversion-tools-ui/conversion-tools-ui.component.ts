import { Component, Input, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ConversionTool } from '../../app_models/conversion-tool.model';

@Component({
    selector: 'app-conversion-tools-ui',
    standalone: true,
    imports: [CommonModule, RouterLink, FormsModule],
    templateUrl: './conversion-tools-ui.component.html',
    styleUrl: './conversion-tools-ui.component.css'
})
export class ConversionToolsUiComponent {
    @Input() tools: ConversionTool[] = [];
    @Input() title: string = '';
    @Input() description: string = '';
    @Input() searchPlaceholder: string = 'Search tools...';

    searchTerm = signal('');

    filteredTools = computed(() => {
        const term = this.searchTerm().toLowerCase();
        if (!term) return this.tools;

        return this.tools.filter(tool =>
            tool.title.toLowerCase().includes(term)
        );
    });

    expandedTools = signal(new Set<string>());

    toggleDescription(event: Event, toolId: string) {
        event.preventDefault();
        event.stopPropagation();

        const currentSet = new Set(this.expandedTools());
        if (currentSet.has(toolId)) {
            currentSet.delete(toolId);
        } else {
            currentSet.add(toolId);
        }
        this.expandedTools.set(currentSet);
    }

    isExpanded(toolId: string): boolean {
        return this.expandedTools().has(toolId);
    }
}
