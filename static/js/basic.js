
function login_form() {
	jQuery(function($) {
		$('#login-warning').click(function (e) {
			$.modal(document.getElementById('login-modal'));
		})
		$('.flip').click(function (e) {
			$('#register-type').toggle();
			//$('#password-type').toggle();
			$('#register-box').toggle();
			//$('#password-box').toggle();
			
			$('#login-button').toggle();
			$('#register-button').toggle();
		})
		
		$.modal(document.getElementById('login-modal'));
	})
}