
function login_form() {
	jQuery(function($) {
		$('#login-warning').click(function (e) {
			$.modal($('#login-modal'));
		})
		$('.flip').click(function (e) {
			$('#register-type').toggle();
			//$('#password-type').toggle();
			$('#register-box').toggle();
			//$('#password-box').toggle();
			
			$('#login-button').toggle();
			$('#register-button').toggle();
		})
		
		$.modal($('#login-modal'));
	})
}

function pad_list() {
	$('#create-challenge').click(function (e) {
		$.modal($('#create-modal'));
	})
	$('#upload-file').click(function (e) {
		loc = "main";
		pad_id = "main";
		name = "main";
		if (window.location.search != "" && window.location.search.substr(0, 2)) {
			pad_id = window.location.search.substr(4);
			name = pad_id.substr(pad_id.indexOf('$')+1);
		}
		$('#upload-location').html(name);
		$('#upload-location-data').val(pad_id)
		$.modal($('#upload-modal'));
	})
	$('#show-files').click(function (e) {
		pad_id = "main";
		if (window.location.search != "" && window.location.search.substr(0, 2)) {
			pad_id = window.location.search.substr(4);
		}
		$('#files-frame').attr('src', '/view/files/?id=' + pad_id);
		$.modal($('#files-modal'));
	})
}

function delete_pad(pad) {
	for (name in pad) {
		$('#delete-pad-name').html(name);
		$('#delete-pad-input').val(pad[name]);
		$.modal($('#delete-modal'));
		break;
	}
}