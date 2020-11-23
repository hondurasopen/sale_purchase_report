from openerp.osv import osv
import datetime
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

class reporte(models.TransientModel):
	_name = "report.account_treasury_forecast.account_treasury_print"
	def render_html(self,cr, uid, ids, data=None, context = None):
		self.cr = cr,
		self.uid = uid
		report_obj = self.pool['report']
		report = report_obj._get_report_from_name(cr,uid,'account_treasury_forecast.account_treasury_print')
		docargs = {
			'doc_ids' : ids,	
			'dos_model' : report.model,
			'docs' : self.pool[report.model].browse(cr,uid,ids,context=context),
			'months_in_range':self.months_in_range,
			'get_months':self.get_months,
			'get_docs_by_moth':self.get_docs_by_moth,
			'has_docs' : self.has_docs,
			'show_mont': self.show_mont,
			'has_proy' : self.has_proy,
			'tot_by_doc' : self.tot_by_doc,		
			}
		return report_obj.render(cr, uid, ids,'account_treasury_forecast.account_treasury_print',docargs,context=context)

	def daterange(start_date,end_date):
		for n in range(int ((end_date - start_date).days)):
			yield start_date + timedelta(n)

	def get_months(self,start_date,end_date):
		start_date = dt.strptime(str(start_date),'%Y-%m-%d')
		months = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
		cont = 1
		result_months = []
		sextena = []
		actual_month = start_date.month
		anio_actual = start_date.year
		values = []
		cont = 1
		flag = False
		x = range(0,self.months_in_range(str(start_date),str(end_date)))
		for n in x:
			if len(x) >= 5 :
				values = []	
				values.append(anio_actual)
				values.append(actual_month)
				if actual_month == 12:
					sextena.append({'dato' : str(months[11])+"["+str(anio_actual)+"]",'dm':values})
					anio_actual = int(anio_actual) + 1
					if n != (len(x)-(len(x)%6)):
						actual_month = 1
				else:
					sextena.append({'dato' : str(months[actual_month-1])+"["+str(anio_actual)+"]",'dm':values})
					if n != (len(x)-(len(x)%6)):
						actual_month += 1
				if cont == 6:
					cont=1
					result_months.append(sextena)
					sextena = []
				else:
					cont += 1
				flag = True
			if n == len(x)-(len(x)%6):
				sextena = []
				for y in range(len(x)-(len(x)%6),len(x)):
					values = []
					values.append(anio_actual)
					values.append(actual_month)
					if actual_month == 12:
						anio_actual = int(anio_actual) - 1
						sextena.append({'dato' : str(months[11])+"["+str(anio_actual)+"]",'dm':values})
						anio_actual = int(anio_actual) + 1
						actual_month = 1
					else:
						sextena.append({'dato' : str(months[actual_month-1])+"["+str(anio_actual)+"]",'dm':values})
						actual_month += 1
				result_months.append(sextena)
				break
		return result_months

	def months_in_range(self,start_date,end_date):
		start_date = dt.strptime(start_date[:10],'%Y-%m-%d')
		end_date = dt.strptime(end_date[:10],'%Y-%m-%d')
		meses_x_anio = (end_date.year - start_date.year)*12
		rest_meses = end_date.month - start_date.month + 1
		if end_date.month == start_date.month:
			rest_meses = 1
		return meses_x_anio + rest_meses
		
	def has_docs(self,acual_data,obj,model):
		fecha = datetime.datetime(acual_data[0],acual_data[1],1)
		
		if model == 'inv' :
			for inv in obj:
				if fecha.month == dt.strptime(str(inv.date_due),'%Y-%m-%d').month and fecha.year == dt.strptime(str(inv.date_due),'%Y-%m-%d').year:
					return True
		elif model in ['rec_lines','req_fonds','checks']:
			for line in obj:
				if fecha.month == dt.strptime(str(line.date),'%Y-%m-%d').month and fecha.year == dt.strptime(str(line.date),'%Y-%m-%d').year:
					return True
		elif model == 'purch_ord':
			for line in obj:
				if fecha.month == dt.strptime(str(line.date_order),'%Y-%m-%d').month and fecha.year == dt.strptime(str(line.date_order),'%Y-%m-%d').year:
					return True
		else:	
			return False
	def get_docs_by_moth(self,acual_data,obj,model):
		fecha = datetime.datetime(acual_data[0],acual_data[1],1)
		if model == 'inv':
			date = dt.strptime(str(obj.date_due),'%Y-%m-%d')
			if fecha.month == date.month and fecha.year == date.year:
				return True
			else:
				return False
		elif model in ['rec_lines','req_fonds','checks']:
			date = dt.strptime(str(obj.date),'%Y-%m-%d')
			if fecha.month == date.month and fecha.year == date.year:
				return True
			else:
				return False
		elif model == 'purch_ord':
			date = dt.strptime(str(obj.date_order),'%Y-%m-%d')
			if fecha.month == date.month and fecha.year == date.year:
				return True
			else:
				return False
		return False

	def has_proy(self,proy):
		if len(proy)>=1:
			return True
		return False


	
	def show_mont(self,o,acual_data):
		if self.has_docs(acual_data, o.out_invoice_ids,'inv'):
			return True
		elif self.has_docs(acual_data, o.in_invoice_ids,'inv'):
			return True
		elif self.has_docs(acual_data, o.recurring_line_ids,'rec_lines'):
			return True
		elif self.has_docs(acual_data, o.funds_req_line_ids,'req_fonds'):
			return True
		elif self.has_docs(acual_data, o.mchecks_line_ids,'checks'):
			return True
		elif self.has_docs(acual_data, o.purchase_order,'purch_ord'):
			return True
		else:
			return False


	def tot_by_doc(self,acual_data,obj,model,o):
		fecha = datetime.datetime(acual_data[0],acual_data[1],1)
		total = 0.0

		if model == 'inv':
			for inv in obj:
				if inv.date_due >= o.start_date and inv.date_due<= o.end_date:
					total+=inv.total_amount					
			return total

		elif model in ['req_fonds','checks']:
			for line in obj:
				if line.date >= o.start_date and line.date <= o.end_date:
					total+=line.total
			return total

		elif model == 'purch_ord':
			for line in obj:
				if line.date_order >= o.start_date and line.date_order <= o.end_date:
					total+=line.amount_total	
			return total

		elif model == 'rec_lines':
			for line in obj:
				if line.date >= o.start_date and line.date <= o.end_date:
					total+=line.amount	
			return total

		else:	
			return False





