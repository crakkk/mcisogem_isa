openerp.mcisogem_isa = function(instance) {

	instance.web.client_actions.add('groupe.action', 'instance.odooweb.Action');

	instance.mcisogem_isa.Action = instance.web.Widget.extend({
		template : 'ajoutgroupe',
		className : 'oe_odoo1',
		init : function(parent, options) {
			this._super(parent);
			var self = this;
		},
		start : function() {
			// this.$el.text("Hello, world!");
			self.display_data();
			return this._super();
		},	
		display_data : function() {

			var self = this;
			// Recuperation des valeurs


		},
	});
};