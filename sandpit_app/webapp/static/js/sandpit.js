$(function () {
    $('a.confirm').click(function (e) {
        e.preventDefault();

        var confirm_data = $(this).data();

        var title = confirm_data.title || 'Are you sure?';
        var body = confirm_data.body || 'Are you sure you sure?';
        var cancel_button = confirm_data.cancelButton || 'Cancel';
        var confirm_button = confirm_data.confirmButton || 'Confirm';
        var action_url = this.href;

        $('#confirmModal').remove();

        var modal = $(
            '<div class="modal fade" id="confirmModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">' +
            '  <div class="modal-dialog">' +
            '    <div class="modal-content">' +
            '      <div class="modal-header">' +
            '        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
            '        <h4 class="modal-title" id="myModalLabel">' + title + '</h4>' +
            '      </div>' +
            '      <div class="modal-body">' +
            '        ' + body +
            '      </div>' +
            '      <div class="modal-footer">' +
            '        <button type="button" class="btn btn-default" data-dismiss="modal">' + cancel_button + '</button>' +
            '        <button type="button" class="btn btn-danger do-confirm">' + confirm_button + '</button>' +
            '        <img class="spinner" src="/static/spinner.gif"/>' +
            '      </div>' +
            '    </div>' +
            '  </div>' +
            '</div>')
        .appendTo('body');

        $('#confirmModal .spinner').toggle();

        $('#confirmModal .do-confirm').click(function (e) {
            $('<form action="'+action_url+'" method="POST" id="confirmSubmitForm"/>').appendTo('#confirmModal');
            $('#confirmModal button').prop('disabled', true);
            $('#confirmModal .spinner').toggle();
            $('#confirmSubmitForm').submit();
        });

        $('#confirmModal').modal();        
    });
});