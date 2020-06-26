from aiohttp import ClientError
from asgiref.sync import async_to_sync
from django.contrib import admin, messages
from django.utils.translation import ngettext

from .models import ContainerSpecs, Sandbox, SandboxExecution, SandboxSpecs, SandboxUsage



@admin.register(Sandbox)
class SandboxAdmin(admin.ModelAdmin):
    """Admin interface for Sandbox."""
    list_display = ('id', 'name', 'url', 'enabled')
    actions = ['enable', 'disable', 'poll_specifications']
    
    
    def enable(self, request, queryset):
        """Allow to enable selected Sandboxes."""
        updated = queryset.update(enabled=True)
        self.message_user(request, ngettext(
            '%d Sandbox was successfully enabled.',
            '%d Sandboxes were successfully enabled.',
            updated,
        ) % updated, messages.SUCCESS)
    
    
    def disable(self, request, queryset):
        """Allows to disable selected Sandboxes."""
        updated = queryset.update(enabled=False)
        self.message_user(request, ngettext(
            '%d Sandbox was successfully disable.',
            '%d Sandboxes were successfully disable.',
            updated,
        ) % updated, messages.SUCCESS)
    
    
    def poll_specifications(self, request, queryset):
        """Poll specifications of selected Sandboxes, if they're enabled."""
        success = failure = disabled = 0
        failure_lst = []
        for sandbox in queryset:
            try:
                if sandbox.enabled:
                    async_to_sync(sandbox.poll_specifications)()
                    success += 1
                else:
                    disabled += 1
            except ClientError:
                failure += 1
                failure_lst.append(str(sandbox))
        
        if success:
            self.message_user(request, ngettext(
                'Successfully polled specifications of %d Sandbox',
                'Successfully polled specifications of %d Sandboxes',
                success,
            ) % success, messages.SUCCESS)
        
        if disabled:
            self.message_user(request, ngettext(
                'Did not polled specifications of %d Sandbox because it was disabled',
                'Did not polled specifications of %d Sandboxes because they were disabled',
                disabled,
            ) % disabled, messages.WARNING)
        
        if failure:
            self.message_user(request, ngettext(
                'Could not join %d Sandbox :' + str(failure_lst),
                'Could not join %d Sandboxes :' + str(failure_lst),
                failure,
            ) % failure, messages.ERROR)
    
    
    enable.short_description = "Enable selected Sandboxes"
    disable.short_description = "Disable selected Sandboxes"
    poll_specifications.short_description = "Poll specifications of selected Sandboxes"



@admin.register(ContainerSpecs)
class ContainerSpecsAdmin(admin.ModelAdmin):
    """Admin interface for ContainerSpecs."""
    list_display = ('id', 'sandbox')



@admin.register(SandboxSpecs)
class SandboxSpecsAdmin(admin.ModelAdmin):
    """Admin interface for SandboxSpecs."""
    list_display = ('id', 'sandbox')



@admin.register(SandboxUsage)
class SandboxUsageAdmin(admin.ModelAdmin):
    """Admin interface for SandboxUsage."""
    list_display = ('id', 'sandbox', 'enabled', 'reached', 'date')



@admin.register(SandboxExecution)
class SandboxExecutionAdmin(admin.ModelAdmin):
    """Admin interface for SandboxExecution."""
    list_display = ('id', 'sandbox', 'date', 'success')
