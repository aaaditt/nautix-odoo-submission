env['res.users'].browse(2).write({'password': 'admin'})
env.cr.commit()
print("Password fully reset via Odoo ORM!")
